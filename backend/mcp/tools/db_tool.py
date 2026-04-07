"""
Database Tool - SQL Server Query Executor (TQSL Protocol)

Provides MCP tools for querying SQL Server databases via ODBC.
Implements TQSL (Think-Query-SQL Server) protocol for safe and efficient database access.
"""

import pyodbc
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from backend.core.config import settings
from backend.core.logger import log


# Connection pool for reusing database connections
_connection_pool: List[pyodbc.Connection] = []
_MAX_POOL_SIZE = 5


@contextmanager
def get_db_connection():
    """
    Context manager for database connections with pooling support.
    Uses TQSL protocol: Think (validate) -> Query (execute) -> SQL Server (respond).
    
    Yields:
        pyodbc.Connection: Active database connection.
    """
    conn = None
    
    # Try to get connection from pool
    if _connection_pool:
        conn = _connection_pool.pop()
        try:
            # Test if connection is still valid
            conn.cursor().execute("SELECT 1")
            log.debug("Reused connection from pool")
        except pyodbc.Error:
            log.warning("Pooled connection expired, creating new one")
            conn = None
    
    # Create new connection if needed
    if conn is None:
        try:
            conn = pyodbc.connect(
                settings.db_connection_string,
                timeout=30,
                autocommit=True  # For read-only queries
            )
            log.debug("New database connection established")
        except pyodbc.Error as e:
            log.error(f"Database connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    try:
        yield conn
    except Exception as e:
        # Don't return broken connections to pool
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        # Return connection to pool if not too large
        if conn and len(_connection_pool) < _MAX_POOL_SIZE:
            try:
                conn.cursor().execute("SELECT 1")  # Keep-alive check
                _connection_pool.append(conn)
            except pyodbc.Error:
                try:
                    conn.close()
                except Exception:
                    pass


def _execute_query(query: str, max_rows: int = 100, params: Optional[tuple] = None) -> Dict[str, Any]:
    """
    Internal helper to execute a query and return structured results.
    
    Args:
        query: SQL query to execute.
        max_rows: Maximum rows to return.
        params: Optional query parameters.
        
    Returns:
        Dictionary with 'columns', 'rows', 'row_count', 'success', and optional 'error'.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names from cursor description
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchmany(max_rows)
            row_count = len(rows)
            
            cursor.close()
            
            return {
                "columns": columns,
                "rows": [dict(zip(columns, row)) for row in rows],
                "row_count": row_count,
                "success": True
            }
            
    except pyodbc.Error as e:
        log.error(f"SQL error: {str(e)}")
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "success": False,
            "error": f"Database error: {str(e)}"
        }
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "success": False,
            "error": f"Error: {str(e)}"
        }


def query_sql(query: str, max_rows: int = 100) -> str:
    """
    Execute a SQL SELECT query against the SQL Server database (TQSL Protocol).
    
    TQSL Protocol ensures:
    1. Think: Validate query is SELECT-only
    2. Query: Execute with row limit and timeout
    3. SQL Server: Return formatted results
    
    Args:
        query: SQL SELECT query to execute (read-only).
        max_rows: Maximum number of rows to return (default: 100, max: 1000).

    Returns:
        Query results formatted as a markdown table.
    """
    # TQSL Step 1: THINK - Validate the query
    query_upper = query.strip().upper()
    blocked_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "EXEC", "GRANT", "REVOKE"]
    
    for keyword in blocked_keywords:
        if query_upper.startswith(keyword) or keyword in query_upper.split():
            log.warning(f"Blocked dangerous query containing: {keyword}")
            return f"Error: Only SELECT queries are allowed. Dangerous keyword '{keyword}' detected."
    
    if not query_upper.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    
    # TQSL Step 2: QUERY - Execute with limits
    max_rows = min(max_rows, 1000)
    log.info(f"TQSL Execute: {query[:100]}... (max_rows: {max_rows})")
    
    result = _execute_query(query, max_rows)
    
    if not result["success"]:
        return result.get("error", "Unknown error occurred")
    
    # TQSL Step 3: SQL Server - Format results
    if result["row_count"] == 0:
        return "Query returned no results."
    
    # Format as markdown table
    columns = result["columns"]
    rows = result["rows"]
    
    # Truncate long values for readability
    max_value_length = 100
    
    header = f"Query Results ({result['row_count']} rows)\n"
    header += "-" * 60 + "\n"
    
    headers_str = "| " + " | ".join(str(c)[:50] for c in columns) + " |\n"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |\n"
    
    data_rows = ""
    for row in rows:
        values = []
        for col in columns:
            val = row.get(col)
            val_str = str(val) if val is not None else "NULL"
            if len(val_str) > max_value_length:
                val_str = val_str[:max_value_length] + "..."
            values.append(val_str)
        data_rows += "| " + " | ".join(values) + " |\n"
    
    return header + headers_str + separator + data_rows


def list_tables() -> str:
    """
    List all tables in the connected SQL Server database (TQSL Protocol).
    
    Returns:
        List of table names with row counts.
    """
    log.info("TQSL: Listing database tables")
    
    query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            p.rows AS row_count
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
        WHERE t.is_ms_shipped = 0
        GROUP BY s.name, t.name, p.rows
        ORDER BY s.name, t.name
    """
    
    result = _execute_query(query)
    
    if not result["success"]:
        return f"Error listing tables: {result.get('error', 'Unknown error')}"
    
    if not result["rows"]:
        return "No tables found in the database."
    
    # Format as markdown table
    output = f"Database Tables ({len(result['rows'])} tables):\n"
    output += "-" * 60 + "\n"
    output += "| Schema | Table | Row Count |\n"
    output += "|--------|-------|-----------|\n"
    
    for row in result["rows"]:
        schema = row.get("schema_name", "dbo")
        table = row.get("table_name", "unknown")
        rows = row.get("row_count", "N/A")
        output += f"| {schema} | {table} | {rows:,} |\n"
    
    log.info(f"TQSL: Found {len(result['rows'])} tables")
    return output


def get_table_info(table_name: str) -> str:
    """
    Get schema information for a specific table (TQSL Protocol).
    
    Args:
        table_name: Name of the table (can include schema, e.g., 'dbo.Users').

    Returns:
        Column names, data types, constraints, and primary keys.
    """
    log.info(f"TQSL: Getting info for table: {table_name}")
    
    # Parse schema.table if provided
    if "." in table_name:
        schema, table = table_name.split(".", 1)
    else:
        schema = "dbo"
        table = table_name
    
    # Query for column information with additional metadata
    query = """
        SELECT 
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            c.COLUMN_DEFAULT,
            pk.is_primary_key
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN (
            SELECT 
                ku.TABLE_SCHEMA,
                ku.TABLE_NAME,
                ku.COLUMN_NAME,
                1 as is_primary_key
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
            INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc 
                ON ku.CONSTRAINT_NAME = tc.CONSTRAINT_NAME 
                AND ku.TABLE_SCHEMA = tc.CONSTRAINT_SCHEMA
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) pk ON c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
            AND c.TABLE_NAME = pk.TABLE_NAME 
            AND c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE c.TABLE_SCHEMA = ? AND c.TABLE_NAME = ?
        ORDER BY c.ORDINAL_POSITION
    """
    
    result = _execute_query(query, params=(schema, table))
    
    if not result["success"]:
        return f"Error getting table info: {result.get('error', 'Unknown error')}"
    
    if not result["rows"]:
        return f"Table '{table_name}' not found."
    
    # Format as markdown table
    output = f"Schema for {table_name} ({len(result['rows'])} columns):\n"
    output += "-" * 80 + "\n"
    output += "| # | Column | Type | Nullable | Max Length | Primary Key | Default |\n"
    output += "|---|--------|------|----------|------------|-------------|---------|\n"
    
    for i, row in enumerate(result["rows"], 1):
        col_name = row.get("COLUMN_NAME", "")
        data_type = row.get("DATA_TYPE", "")
        is_nullable = "YES" if row.get("IS_NULLABLE") == "YES" else "NO"
        
        # Format max length
        max_length = row.get("CHARACTER_MAXIMUM_LENGTH")
        precision = row.get("NUMERIC_PRECISION")
        scale = row.get("NUMERIC_SCALE")
        
        if max_length:
            length_str = str(max_length) if max_length != -1 else "MAX"
        elif precision:
            length_str = f"{precision},{scale}" if scale else str(precision)
        else:
            length_str = "-"
        
        is_pk = "PK" if row.get("is_primary_key") else ""
        default = row.get("COLUMN_DEFAULT") or "-"
        
        # Truncate long defaults
        if len(str(default)) > 30:
            default = str(default)[:27] + "..."
        
        output += f"| {i} | {col_name} | {data_type} | {is_nullable} | {length_str} | {is_pk} | {default} |\n"
    
    log.info(f"TQSL: Retrieved {len(result['rows'])} columns for {table_name}")
    return output


def search_columns(column_pattern: str, table_pattern: Optional[str] = None) -> str:
    """
    Search for columns by name pattern across tables (TQSL Protocol).
    Useful for discovering tables that contain specific data.
    
    Args:
        column_pattern: Column name to search for (supports % wildcards).
        table_pattern: Optional table name filter (supports % wildcards).

    Returns:
        List of tables and columns matching the pattern.
    """
    log.info(f"TQSL: Searching for columns matching '{column_pattern}'")
    
    query = """
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME LIKE ?
    """
    
    params = [f"%{column_pattern}%"]
    
    if table_pattern:
        query += " AND TABLE_NAME LIKE ?"
        params.append(f"%{table_pattern}%")
    
    query += " ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION"
    
    # Execute with parameters using the internal helper
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, *params)
            columns_data = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                return f"No columns found matching pattern '{column_pattern}'."
            
            output = f"Columns matching '{column_pattern}' ({len(rows)} found):\n"
            output += "-" * 60 + "\n"
            output += "| Schema | Table | Column | Type | Nullable |\n"
            output += "|--------|-------|--------|------|----------|\n"
            
            for row in rows:
                output += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n"
            
            log.info(f"TQSL: Found {len(rows)} matching columns")
            return output
            
    except pyodbc.Error as e:
        log.error(f"Search error: {str(e)}")
        return f"Error: {str(e)}"


def register_db_tools(mcp) -> None:
    """Register database query tools with MCP server (TQSL Protocol)."""
    
    @mcp.tool()
    def query_sql_mcp(query: str, max_rows: int = 100) -> str:
        """Execute a SQL SELECT query (TQSL Protocol: Think-Query-SQL Server)."""
        return query_sql(query, max_rows)

    @mcp.tool()
    def list_tables_mcp() -> str:
        """List all tables in the database (TQSL Protocol)."""
        return list_tables()

    @mcp.tool()
    def get_table_info_mcp(table_name: str) -> str:
        """Get schema information for a table (TQSL Protocol)."""
        return get_table_info(table_name)

    @mcp.tool()
    def search_columns_mcp(column_pattern: str, table_pattern: str = None) -> str:
        """Search for columns by name pattern across tables (TQSL Protocol)."""
        return search_columns(column_pattern, table_pattern)