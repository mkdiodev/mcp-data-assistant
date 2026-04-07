"""
Database Tool - SQL Server Query Executor

Provides MCP tools for querying SQL Server databases via ODBC.
"""

import pyodbc
from typing import Optional
from fastmcp import FastMCP
from backend.core.config import settings
from backend.core.logger import log


def get_db_connection() -> pyodbc.Connection:
    """Create and return a database connection."""
    try:
        conn = pyodbc.connect(settings.db_connection_string)
        log.debug("Database connection established")
        return conn
    except pyodbc.Error as e:
        log.error(f"Database connection error: {str(e)}")
        raise


def query_sql(query: str, max_rows: int = 100) -> str:
    """
    Execute a SQL SELECT query against the database.

    Args:
        query: SQL SELECT query to execute (read-only).
        max_rows: Maximum number of rows to return (default: 100, max: 1000).

    Returns:
        Query results formatted as a markdown table.
    """
    # Security: Only allow SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    # Limit max rows for safety
    max_rows = min(max_rows, 1000)

    log.info(f"Executing SQL query (max_rows: {max_rows})")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute query with row limit
        cursor.execute(query)

        # Get column names
        columns = [column[0] for column in cursor.description]

        # Fetch results
        rows = cursor.fetchmany(max_rows)

        if not rows:
            return "Query returned no results."

        # Format as markdown table
        header = f"Query Results ({len(rows)} rows)\n"
        header += "-" * 60 + "\n"

        # Create markdown table
        headers_str = "| " + " | ".join(columns) + " |\n"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"
        data_rows = ""
        for row in rows:
            values = [str(v) if v is not None else "NULL" for v in row]
            data_rows += "| " + " | ".join(values) + " |\n"

        result = header + headers_str + separator + data_rows

        cursor.close()
        conn.close()

        log.info(f"Query returned {len(rows)} rows")
        return result

    except pyodbc.Error as e:
        log.error(f"SQL error: {str(e)}")
        return f"Database error: {str(e)}"
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"


def list_tables() -> str:
    """
    List all tables in the connected database.

    Returns:
        List of table names.
    """
    log.info("Listing database tables")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all user tables
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)

        tables = cursor.fetchall()

        if not tables:
            return "No tables found in the database."

        result = "Database Tables:\n"
        for schema, table in tables:
            result += f"- {schema}.{table}\n"

        cursor.close()
        conn.close()

        log.info(f"Found {len(tables)} tables")
        return result

    except pyodbc.Error as e:
        log.error(f"Error listing tables: {str(e)}")
        return f"Database error: {str(e)}"
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"


def get_table_info(table_name: str) -> str:
    """
    Get schema information for a specific table.

    Args:
        table_name: Name of the table (can include schema, e.g., 'dbo.Users').

    Returns:
        Column names, data types, and constraints.
    """
    log.info(f"Getting info for table: {table_name}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parse schema.table if provided
        if "." in table_name:
            schema, table = table_name.split(".", 1)
        else:
            schema = "dbo"
            table = table_name

        # Get column information
        cursor.execute("""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, schema, table)

        columns = cursor.fetchall()

        if not columns:
            return f"Table '{table_name}' not found."

        result = f"Schema for {table_name}:\n"
        result += "-" * 60 + "\n"
        result += f"| Column | Type | Nullable | Max Length |\n"
        result += f"|--------|------|----------|------------|\n"

        for col in columns:
            col_name, data_type, is_nullable, max_length = col
            nullable = "YES" if is_nullable == "YES" else "NO"
            length = str(max_length) if max_length else "-"
            result += f"| {col_name} | {data_type} | {nullable} | {length} |\n"

        cursor.close()
        conn.close()

        log.info(f"Retrieved {len(columns)} columns for {table_name}")
        return result

    except pyodbc.Error as e:
        log.error(f"Error getting table info: {str(e)}")
        return f"Database error: {str(e)}"
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"


def register_db_tools(mcp: FastMCP) -> None:
    """Register database query tools with MCP server."""

    @mcp.tool()
    def query_sql_mcp(query: str, max_rows: int = 100) -> str:
        return query_sql(query, max_rows)

    @mcp.tool()
    def list_tables_mcp() -> str:
        return list_tables()

    @mcp.tool()
    def get_table_info_mcp(table_name: str) -> str:
        return get_table_info(table_name)