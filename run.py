import os
import platform
import subprocess
import sys
import uvicorn

from app.config import settings

def activate_venv():
    """Ensure we're running in the virtual environment"""
    # Check if we're already in a virtual environment
    in_venv = (
        hasattr(sys, "real_prefix") or
        (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    )

    if not in_venv:
        print("Activating virtual environment...")

        venv_dir = "venv"
        if platform.system() == "Windows":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")

        if not os.path.exists(python_path):
            print("Virtual environment not found. Please run setup.py first.")
            sys.exit(1)

        # Re-run this script with the virtual environment's Python
        os.execl(python_path, python_path, *sys.argv)
    else:
        print("Already in virtual environment.")

def main():
    """Run the FastAPI application"""
    print(f"Starting {settings.APP_NAME}...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Server running at http://{settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    activate_venv()
    main()
