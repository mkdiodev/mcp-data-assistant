"""
FastAPI Application - Main Entry Point

Handles HTTP requests and communicates with LM Studio for AI inference.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
from openai import AsyncOpenAI
import json

from backend.core.config import settings
from backend.core.logger import log
from backend.core.prompts import SYSTEM_PROMPT, DATABASE_PROTOCOL, TOOLS_INSTRUCTIONS
from backend.mcp.server import mcp
from backend.mcp.tools.file_tool import list_data_files, read_excel_csv, get_file_columns
from backend.mcp.tools.db_tool import query_sql, list_tables, get_table_info, search_columns

# Tool registry mapping tool names to their functions and metadata
TOOL_REGISTRY = {
    "list_data_files": {
        "func": list_data_files,
        "description": "List all Excel and CSV files in the data folder",
        "parameters": {"properties": {}},
    },
    "read_excel_csv": {
        "func": read_excel_csv,
        "description": "Read an Excel or CSV file",
        "parameters": {
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to read"},
                "sheet_name": {"type": "string", "description": "Sheet name for Excel files"},
                "nrows": {"type": "integer", "description": "Number of rows to read"},
            },
            "required": ["filename"],
        },
    },
    "get_file_columns": {
        "func": get_file_columns,
        "description": "Get column names and types from a file",
        "parameters": {
            "properties": {
                "filename": {"type": "string", "description": "Name of the file"},
            },
            "required": ["filename"],
        },
    },
    "query_sql": {
        "func": query_sql,
        "description": "Execute a SQL SELECT query (TQSL Protocol: Step 3 - Run after checking tables and schema)",
        "parameters": {
            "properties": {
                "query": {"type": "string", "description": "SQL SELECT query"},
                "max_rows": {"type": "integer", "description": "Maximum rows to return"},
            },
            "required": ["query"],
        },
    },
    "list_tables": {
        "func": list_tables,
        "description": "List all tables in the database with row counts (TQSL Protocol: Step 1 - Always check first)",
        "parameters": {"properties": {}},
    },
    "get_table_info": {
        "func": get_table_info,
        "description": "Get schema information for a table including column types and primary keys (TQSL Protocol: Step 2)",
        "parameters": {
            "properties": {
                "table_name": {"type": "string", "description": "Name of the table"},
            },
            "required": ["table_name"],
        },
    },
    "search_columns": {
        "func": search_columns,
        "description": "Search for columns by name pattern across tables (TQSL Protocol: Discovery tool)",
        "parameters": {
            "properties": {
                "column_pattern": {"type": "string", "description": "Column name pattern to search for"},
                "table_pattern": {"type": "string", "description": "Optional table name pattern to filter"},
            },
            "required": ["column_pattern"],
        },
    },
}

app = FastAPI(
    title="MCP Data Assistant API",
    description="Backend API for MCP Data Assistant with AI and MCP integration",
    version="0.1.0",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize async OpenAI client for LM Studio
client = AsyncOpenAI(
    base_url=settings.ai_base_url,
    api_key=settings.ai_api_key,
)


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    tool_calls: Optional[List[dict]] = []


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "MCP Data Assistant API"}


@app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    tools_info = []
    for name, info in TOOL_REGISTRY.items():
        tools_info.append({
            "name": name,
            "description": info["description"],
        })
    return {"tools": tools_info}


async def execute_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Execute an MCP tool with given arguments."""
    log.info(f"Executing MCP tool: {tool_name} with args: {arguments}")

    try:
        # Get the tool from registry
        tool_entry = TOOL_REGISTRY.get(tool_name)
        if not tool_entry:
            return f"Tool not found: {tool_name}"

        # Call the tool's function with arguments
        func = tool_entry["func"]
        result = func(**arguments)
        return result
    except Exception as e:
        log.error(f"Error executing tool {tool_name}: {str(e)}")
        return f"Error executing tool: {str(e)}"


async def handle_tool_calls(response, messages: list) -> str:
    """Process tool calls from AI response and return results."""
    tool_results = []

    if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Execute the tool
            result = await execute_mcp_tool(tool_name, arguments)
            tool_results.append({"tool": tool_name, "result": result})

            # Add tool result as a message for the AI
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # Get AI response with tool results
        second_response = await client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
        )

        return second_response.choices[0].message.content

    return response.choices[0].message.content


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Receives user message, processes with AI, and returns response.
    The AI can call MCP tools for file reading and database queries.
    """
    log.info(f"Received chat request: {request.message[:50]}...")

    try:
        # Build messages array with system prompts from files
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT + "\n\n" + DATABASE_PROTOCOL + "\n\n" + TOOLS_INSTRUCTIONS,
            }
        ]

        # Add conversation history
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # Get AI response with tool definitions
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_data_files",
                    "description": "List all Excel and CSV files in the data folder",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_excel_csv",
                    "description": "Read an Excel or CSV file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file to read"},
                            "sheet_name": {"type": "string", "description": "Sheet name for Excel files"},
                            "nrows": {"type": "integer", "description": "Number of rows to read"},
                        },
                        "required": ["filename"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_columns",
                    "description": "Get column names and types from a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file"},
                        },
                        "required": ["filename"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tables",
                    "description": "TQSL Step 1: List all tables in the database with row counts. ALWAYS call this first before any SQL query.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_table_info",
                    "description": "TQSL Step 2: Get schema information for a table. ALWAYS call this before query_sql to verify columns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string", "description": "Name of the table"},
                        },
                        "required": ["table_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_columns",
                    "description": "TQSL Discovery: Search for columns by name pattern across tables. Use when user asks about data you haven't seen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "column_pattern": {"type": "string", "description": "Column name pattern to search for"},
                            "table_pattern": {"type": "string", "description": "Optional table name pattern to filter"},
                        },
                        "required": ["column_pattern"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_sql",
                    "description": "TQSL Step 3: Execute a SQL SELECT query. ONLY call after list_tables and get_table_info confirm the schema.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL SELECT query"},
                            "max_rows": {"type": "integer", "description": "Maximum rows to return"},
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        response = await client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
            tools=tools,
        )

        # Check if AI wants to call any tools
        final_response = await handle_tool_calls(response, messages)

        log.info("Response sent successfully")
        return ChatResponse(
            response=final_response,
            tool_calls=[],
        )

    except httpx.ConnectError:
        log.error("Cannot connect to LM Studio")
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to AI server (LM Studio). Please ensure it's running on port 1234.",
        )
    except Exception as e:
        log.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/list")
async def api_list_files():
    """Direct API endpoint to list files (bypassing AI)."""
    from backend.mcp.tools.file_tool import list_data_files
    return {"files": list_data_files()}


@app.get("/api/files/{filename}")
async def api_read_file(filename: str, nrows: int = 10):
    """Direct API endpoint to read a file (bypassing AI)."""
    from backend.mcp.tools.file_tool import read_excel_csv
    result = read_excel_csv(filename, nrows=nrows)
    return {"content": result}


@app.get("/api/tables")
async def api_list_tables():
    """Direct API endpoint to list database tables."""
    from backend.mcp.tools.db_tool import list_tables
    result = list_tables()
    return {"content": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )