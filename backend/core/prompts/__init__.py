"""
Prompt Modules - System Prompts for AI Assistant

This module provides system prompts that are loaded from text files.
Separating prompts from code makes them easier to maintain, test, and version control.

Usage:
    from backend.core.prompts.system_prompt import SYSTEM_PROMPT
    from backend.core.prompts.database_protocol import DATABASE_PROTOCOL
    from backend.core.prompts.tools_instructions import TOOLS_INSTRUCTIONS
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env file if exists
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def _read_prompt_file(filename: str) -> str:
    """
    Read a prompt from the prompts directory.
    
    Args:
        filename: Name of the prompt file (without .txt extension).
                 Supported files: system_prompt, database_protocol, tools_instructions
    
    Returns:
        Prompt content as string.
    """
    base_path = Path(__file__).parent.parent
    prompts_dir = base_path / "prompts"
    prompt_file = prompts_dir / f"{filename}.txt"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    return prompt_file.read_text(encoding="utf-8")


# System Prompt - Main AI behavior and tool descriptions
SYSTEM_PROMPT = _read_prompt_file("system_prompt")

# Database Protocol - TQSL Think-Query-SQL Server protocol
DATABASE_PROTOCOL = _read_prompt_file("database_protocol")

# Tools Instructions - Detailed usage instructions for each tool
TOOLS_INSTRUCTIONS = _read_prompt_file("tools_instructions")
