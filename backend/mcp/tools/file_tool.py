"""
File Tool - Excel and CSV Reader

Provides MCP tools for reading Excel and CSV files from the data folder.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from backend.core.config import settings
from backend.core.logger import log


def list_data_files() -> str:
    """
    List all Excel and CSV files available in the data folder.

    Returns:
        String containing list of available files.
    """
    log.info("Listing available data files")
    data_path = settings.data_path

    if not data_path.exists():
        return f"Data folder not found: {data_path}"

    # Find all Excel and CSV files
    extensions = (".xlsx", ".xls", ".csv")
    files = [f.name for f in data_path.iterdir() if f.suffix.lower() in extensions]

    if not files:
        return "No Excel or CSV files found in data folder."

    result = "Available files:\n"
    for f in sorted(files):
        result += f"- {f}\n"

    log.info(f"Found {len(files)} data files")
    return result


def read_excel_csv(
    filename: str,
    sheet_name: Optional[str] = None,
    nrows: Optional[int] = None,
) -> str:
    """
    Read an Excel or CSV file and return its contents as a formatted table.

    Args:
        filename: Name of the file to read (e.g., 'data.xlsx', 'sales.csv').
        sheet_name: Sheet name for Excel files (default: first sheet).
        nrows: Number of rows to read (default: all rows).

    Returns:
        Formatted string with tabular data.
    """
    log.info(f"Reading file: {filename} (rows: {nrows})")
    data_path = settings.data_path
    file_path = data_path / filename

    if not file_path.exists():
        return f"File not found: {filename}"

    try:
        # Read file based on extension
        ext = file_path.suffix.lower()

        if ext == ".csv":
            df = pd.read_csv(file_path, nrows=nrows)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=nrows)
        else:
            return f"Unsupported file format: {ext}"

        if df.empty:
            return "File is empty or contains no data."

        # Format output
        total_rows = len(df)
        total_cols = len(df.columns)
        header = f"File: {filename} | Rows: {total_rows} | Columns: {total_cols}\n"
        header += "-" * 60 + "\n"

        # Convert to markdown table
        table = df.to_markdown(index=False)

        result = header + table

        if nrows and total_rows > nrows:
            result += f"\n\n... (showing first {nrows} of {total_rows} rows)"

        log.info(f"Successfully read {len(df)} rows from {filename}")
        return result

    except Exception as e:
        log.error(f"Error reading file {filename}: {str(e)}")
        return f"Error reading file: {str(e)}"


def get_file_columns(filename: str) -> str:
    """
    Get column names and data types from a file.

    Args:
        filename: Name of the file to inspect.

    Returns:
        List of column names with their data types.
    """
    log.info(f"Getting columns from file: {filename}")
    data_path = settings.data_path
    file_path = data_path / filename

    if not file_path.exists():
        return f"File not found: {filename}"

    try:
        ext = file_path.suffix.lower()

        if ext == ".csv":
            df = pd.read_csv(file_path, nrows=0)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, nrows=0)
        else:
            return f"Unsupported file format: {ext}"

        result = f"Columns in {filename}:\n"
        for col, dtype in df.dtypes.items():
            result += f"- {col} ({dtype})\n"

        log.info(f"Retrieved {len(df.columns)} columns from {filename}")
        return result

    except Exception as e:
        log.error(f"Error getting columns from {filename}: {str(e)}")
        return f"Error: {str(e)}"


def register_file_tools(mcp: FastMCP) -> None:
    """Register file reading tools with MCP server."""

    # Create wrapper functions that preserve docstrings for MCP registration
    @mcp.tool()
    def list_data_files_mcp() -> str:
        return list_data_files()

    @mcp.tool()
    def read_excel_csv_mcp(
        filename: str,
        sheet_name: Optional[str] = None,
        nrows: Optional[int] = None,
    ) -> str:
        return read_excel_csv(filename, sheet_name, nrows)

    @mcp.tool()
    def get_file_columns_mcp(filename: str) -> str:
        return get_file_columns(filename)