import os
import platform
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("Creating .env file from .env.example...")
        with open(".env.example", "r") as example_file:
            with open(".env", "w") as env_file:
                env_file.write(example_file.read())
        print("Created .env file. Please update it with your settings.")
    elif not os.path.exists(".env.example"):
        print("Error: .env.example file not found.")
        sys.exit(1)

def setup_virtual_environment():
    """Set up a virtual environment if it doesn't exist"""
    venv_dir = "venv"
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Virtual environment created.")
    else:
        print(f"Virtual environment already exists in {venv_dir}.")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("Installing dependencies...")

    # Determine the Python executable in the virtual environment
    if platform.system() == "Windows":
        python_executable = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_executable = os.path.join("venv", "bin", "python")

    # Install dependencies
    subprocess.run([python_executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("Dependencies installed.")

def setup_database():
    """Set up the database using Alembic"""
    print("Setting up database...")

    try:
        # Create migrations directory if it doesn't exist
        migrations_dir = Path("migrations")
        if not migrations_dir.exists():
            migrations_dir.mkdir(exist_ok=True)

        # Determine the alembic executable path
        if platform.system() == "Windows":
            alembic_executable = os.path.join("venv", "Scripts", "alembic.exe")
        else:
            alembic_executable = os.path.join("venv", "bin", "alembic")

        # Initialize Alembic if not already initialized
        if not os.path.exists("alembic.ini"):
            # Initialize Alembic
            subprocess.run([alembic_executable, "init", "migrations"], check=True)

            # Update alembic.ini with the database URL
            with open("alembic.ini", "r") as file:
                content = file.read()

            # Replace the sqlalchemy.url line
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                "sqlalchemy.url = postgresql://postgres:password@localhost:5432/fastbase"
            )

            with open("alembic.ini", "w") as file:
                file.write(content)

            # Update env.py to use the DATABASE_URL from settings
            env_py_path = os.path.join("migrations", "env.py")
            with open(env_py_path, "r") as file:
                content = file.read()

            # Add import for models to ensure they're available for autogenerate
            if "from app.models import *" not in content:
                content = content.replace(
                    "from alembic import context",
                    "from alembic import context\nfrom app.models import *"
                )

            # Add target_metadata assignment
            if "from app.database import Base" not in content:
                content = content.replace(
                    "# target_metadata = mymodel.Base.metadata",
                    "from app.database import Base\ntarget_metadata = Base.metadata"
                )

            with open(env_py_path, "w") as file:
                file.write(content)

        print("Database configuration complete.")
        print("Note: To create and apply migrations, run the following commands:")
        print(f"  {alembic_executable} revision --autogenerate -m \"Initial migration\"")
        print(f"  {alembic_executable} upgrade head")
        print("You'll need to have PostgreSQL running with the appropriate database created.")

    except Exception as e:
        print(f"Error setting up database: {e}")
        print("You can manually set up the database later.")

    print("Database setup instructions complete.")

def main():
    """Main setup function"""
    print("Setting up FastBase...")

    # Create .env file
    create_env_file()

    # Set up virtual environment
    setup_virtual_environment()

    # Install dependencies
    install_dependencies()

    # Set up database
    setup_database()

    print("\nSetup complete! You can now run the application with: python run.py")

if __name__ == "__main__":
    main()
