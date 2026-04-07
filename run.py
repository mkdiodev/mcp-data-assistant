#!/usr/bin/env python
"""
MCP Data Assistant - Application Runner

Run both backend and frontend from a single command.
Usage:
    python run.py              # Run both backend and frontend
    python run.py --backend    # Run backend only
    python run.py --frontend   # Run frontend only
"""

import subprocess
import sys
import os
import time
import signal
import argparse
from pathlib import Path


# ============================================
# Configuration
# ============================================

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 8501

# Colors for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def print_banner():
    """Print application banner."""
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  🤖 MCP Data Assistant")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    print(f"  {Colors.GREEN}Backend:{Colors.ENDC}  http://localhost:{BACKEND_PORT}")
    print(f"  {Colors.GREEN}API Docs:{Colors.ENDC} http://localhost:{BACKEND_PORT}/docs")
    print(f"  {Colors.GREEN}Frontend:{Colors.ENDC} http://localhost:{FRONTEND_PORT}")
    print()
    print(f"  {Colors.YELLOW}Press Ctrl+C to stop all services{Colors.ENDC}")
    print()


def print_status(service: str, message: str, color: str = Colors.GREEN):
    """Print status message with color."""
    print(f"{color}[{service}]{Colors.ENDC} {message}")


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print(f"{Colors.RED}Error: Python 3.11+ is required{Colors.ENDC}")
        sys.exit(1)


def check_dependencies():
    """Check if required packages are installed."""
    required = ['fastapi', 'uvicorn', 'streamlit', 'httpx']
    missing = []

    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"{Colors.RED}Missing dependencies: {', '.join(missing)}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Run: pip install -r requirements.txt{Colors.ENDC}")
        return False
    return True


def check_env_file():
    """Check if .env file exists."""
    env_path = Path("backend/.env")
    if not env_path.exists():
        print(f"{Colors.YELLOW}Warning: backend/.env not found{Colors.ENDC}")
        print(f"{Colors.DIM}Copy backend/.env.example to backend/.env and configure it{Colors.ENDC}")
        return False
    return True


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    import urllib.request
    import urllib.error

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.getcode() == 200:
                return True
        except (urllib.error.URLError, ConnectionRefusedError):
            pass
        time.sleep(0.5)
    return False


def start_backend():
    """Start the FastAPI backend server."""
    print_status("Backend", "Starting FastAPI server...")

    # Set environment variable for Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())

    # Start uvicorn
    process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", BACKEND_HOST,
            "--port", str(BACKEND_PORT),
            "--reload",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    return process


def start_frontend():
    """Start the Streamlit frontend."""
    print_status("Frontend", "Starting Streamlit server...")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())

    process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", str(FRONTEND_PORT),
            "--server.headless", "true",
            "--server.address", "localhost",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    return process


def stream_output(process, prefix, color):
    """Stream output from a subprocess."""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        line = line.strip()
        if line:
            print(f"{color}[{prefix}]{Colors.ENDC} {line}")


def cleanup(processes):
    """Clean up all running processes."""
    print(f"\n{Colors.YELLOW}Shutting down services...{Colors.ENDC}")

    for proc in processes:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    print(f"{Colors.GREEN}All services stopped.{Colors.ENDC}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Data Assistant Runner")
    parser.add_argument("--backend", action="store_true", help="Run backend only")
    parser.add_argument("--frontend", action="store_true", help="Run frontend only")
    args = parser.parse_args()

    # Check Python version
    check_python_version()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check .env file
    check_env_file()

    # Print banner
    print_banner()

    processes = []

    try:
        # Start backend
        if not args.frontend:
            backend = start_backend()
            processes.append(backend)

            # Wait for backend to be ready
            print_status("Backend", "Waiting for server to be ready...")
            if wait_for_server(f"http://localhost:{BACKEND_PORT}/health"):
                print_status("Backend", "Server is ready!", Colors.GREEN)
            else:
                print_status("Backend", "Server may still be starting...", Colors.YELLOW)

        # Start frontend
        if not args.backend:
            frontend = start_frontend()
            processes.append(frontend)

        # Stream output from all processes
        import threading

        def stream_thread(process, prefix, color):
            """Thread function to stream output."""
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    print(f"{color}[{prefix}]{Colors.ENDC} {line}")
                else:
                    break

        # Create threads for each process
        threads = []
        for proc in processes:
            prefix = "Backend" if proc == backend else "Frontend"
            color = Colors.CYAN if proc == backend else Colors.BLUE
            t = threading.Thread(target=stream_thread, args=(proc, prefix, color), daemon=True)
            t.start()
            threads.append(t)

        # Keep main thread alive
        print(f"{Colors.GREEN}All services running. Press Ctrl+C to stop.{Colors.ENDC}\n")

        while True:
            time.sleep(1)
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"{Colors.RED}A service has stopped unexpectedly{Colors.ENDC}")
                    cleanup(processes)
                    sys.exit(1)

    except KeyboardInterrupt:
        cleanup(processes)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        cleanup(processes)
        sys.exit(1)


if __name__ == "__main__":
    main()