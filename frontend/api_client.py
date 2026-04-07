"""
API Client for Backend Communication

Handles HTTP requests to the FastAPI backend.
"""

import httpx
from typing import Optional
from datetime import datetime


class BackendClient:
    """Client for communicating with the MCP Data Assistant backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 60.0  # Longer timeout for AI inference

    async def health_check(self) -> dict:
        """Check if backend is healthy."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def send_message(self, message: str, history: list = None) -> dict:
        """
        Send a message to the AI and get response.

        Args:
            message: User message
            history: List of previous messages

        Returns:
            Dictionary with 'response' key containing AI response
        """
        payload = {
            "message": message,
            "history": history or [],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def list_files(self) -> list:
        """List available data files."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/files/list")
            response.raise_for_status()
            return response.json().get("files", [])

    async def read_file(self, filename: str, nrows: int = 20) -> dict:
        """Read a file directly."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/files/{filename}",
                params={"nrows": nrows},
            )
            response.raise_for_status()
            return response.json()