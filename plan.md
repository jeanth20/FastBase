can you help setup a template for me using postgres, fastapi and jinja template 

the template should have a login page and a register page and a homepage
when the user logs in there should be a dashboard page and a logout button
we need middleware to record the user's activity
data should be stored in a postgres database 

can you create a folder for the models, routes, services, templates and static files

can we model it in a way that it can be used as a base for other projects similar to 'pocketbase'

I will need a setup and run file for any os 

I want this template to be a base for me to quickly build other projects on top of it


Detailed Plan
I'll create a project structure called "FastBase" (similar to "pocketbase") with the following components:

Project Structure:
app/ - Main application directory
models/ - Database models
routes/ - API routes
services/ - Business logic
middleware/ - Custom middleware
templates/ - Jinja templates
static/ - Static files (CSS, JS, images)
utils/ - Utility functions
config.py - Configuration settings
database.py - Database connection
dependencies.py - FastAPI dependencies
migrations/ - Database migrations
tests/ - Unit and integration tests
setup.py - Setup script
run.py - Script to run the application
requirements.txt - Python dependencies
README.md - Project documentation
.env.example - Example environment variables
Features to implement:
User authentication (login, register, logout)
User activity logging middleware
PostgreSQL database integration
Dashboard page for logged-in users
Homepage for all users
Setup and run files:
Cross-platform setup script
Cross-platform run script



Summary
I've created a comprehensive template project called "FastBase" using FastAPI, PostgreSQL, and Jinja templates. The project includes:

User Authentication:
Login and registration pages
JWT token-based authentication
Secure password hashing
User Activity Tracking:
Middleware to record user activities
Activity display on the dashboard
Database Integration:
PostgreSQL database connection
SQLAlchemy ORM models
Alembic migrations
Frontend:
Responsive design with CSS
Jinja2 templates for server-side rendering
Basic JavaScript functionality
Project Structure:
Organized into models, routes, services, middleware, templates, and static files
Modular design for easy extension
Cross-Platform Setup and Run Scripts:
Windows batch files (.bat)
Unix/Linux shell scripts (.sh)
Python setup script for environment and database setup
How to Use This Template
Setup:
On Windows: Run setup.bat
On Unix/Linux/Mac: Run ./setup.sh (you may need to make it executable with chmod +x setup.sh)
This will create a virtual environment, install dependencies, and set up the database
Run:
On Windows: Run run.bat
On Unix/Linux/Mac: Run ./run.sh (you may need to make it executable with chmod +x run.sh)
The application will be available at http://localhost:8000
Customization:
Update the .env file with your specific settings
Add new models to the app/models directory
Add new routes to the app/routes directory
Add new services to the app/services directory
Customize the templates in the app/templates directory
Add your own CSS and JavaScript in the app/static directory
This template is designed to be a solid foundation for building web applications with FastAPI, PostgreSQL, and Jinja templates. It follows best practices for project structure and includes essential features like authentication and activity tracking.

Would you like me to explain any specific part of the template in more detail?