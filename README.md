# FastBase

A template project using FastAPI, PostgreSQL, and Jinja templates that can serve as a base for quickly building web applications.

![Screenshot 2025-05-16 185146](https://github.com/user-attachments/assets/72f52eb8-2bd5-4547-9636-f11221330735)

## Features

- User authentication (login, register, logout)
- Admin account management
  - First registered user automatically becomes an admin
  - Admins can create other admin accounts
  - Admin dashboard with user management
- Security features
  - Rate limiting middleware for DoS protection
  - Security headers middleware
  - CSRF protection
  - User activity logging middleware
- PostgreSQL database integration with Alembic migrations
- Dashboard page for logged-in users
- Notification system
- UI Components showcase
- Homepage for all users
- Structured project layout for scalability

## Project Structure

```
fastbase/
├── app/
│   ├── models/       # Database models
│   ├── routes/       # API routes
│   ├── services/     # Business logic
│   ├── middleware/   # Custom middleware
│   ├── templates/    # Jinja templates
│   ├── static/       # Static files (CSS, JS, images)
│   ├── utils/        # Utility functions
│   ├── config.py     # Configuration settings
│   ├── database.py   # Database connection
│   └── dependencies.py # FastAPI dependencies
├── migrations/       # Database migrations
├── tests/            # Unit and integration tests
├── setup.py          # Setup script
├── run.py            # Script to run the application
├── requirements.txt  # Python dependencies
├── README.md         # Project documentation
└── .env.example      # Example environment variables
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database

## Setup

### Windows

1. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Run the setup script:
   ```
   setup.bat
   ```

   Or manually:
   ```
   python setup.py
   ```

### Unix/MacOS

1. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Run the setup script:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually:
   ```
   python3 setup.py
   ```

### Database Setup

1. Create a PostgreSQL database named `fastbase`
2. Update the database connection string in your `.env` file
3. Run the following commands to create and apply migrations:
   ```
   # Windows
   venv\Scripts\alembic.exe revision --autogenerate -m "Initial migration"
   venv\Scripts\alembic.exe upgrade head

   # Unix/MacOS
   venv/bin/alembic revision --autogenerate -m "Initial migration"
   venv/bin/alembic upgrade head
   ```

## Running the Application

### Windows

```
run.bat
```

Or manually:
```
python run.py
```

### Unix/MacOS

```
chmod +x run.sh
./run.sh
```

Or manually:
```
python3 run.py
```

The application will be available at: http://localhost:8000

## Detailed Documentation

### Database Management with Alembic

FastBase uses Alembic for database migrations, which allows you to:
- Track changes to your database schema
- Apply and roll back changes
- Generate migration scripts automatically

#### Key Alembic Commands

1. **Create a new migration**:
   ```
   # Windows
   venv\Scripts\alembic.exe revision --autogenerate -m "Description of changes"

   # Unix/MacOS
   venv/bin/alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**:
   ```
   # Windows
   venv\Scripts\alembic.exe upgrade head

   # Unix/MacOS
   venv/bin/alembic upgrade head
   ```

3. **Downgrade to a previous version**:
   ```
   # Windows
   venv\Scripts\alembic.exe downgrade -1

   # Unix/MacOS
   venv/bin/alembic downgrade -1
   ```

4. **View migration history**:
   ```
   # Windows
   venv\Scripts\alembic.exe history

   # Unix/MacOS
   venv/bin/alembic history
   ```

#### Workflow for Database Changes

1. Modify your SQLAlchemy models in `app/models/`
2. Generate a migration script with `alembic revision --autogenerate`
3. Review the generated script in `migrations/versions/`
4. Apply the migration with `alembic upgrade head`

#### Tips for Alembic Usage

- Always review auto-generated migrations before applying them
- For complex changes, consider writing manual migrations
- Keep migrations small and focused on specific changes
- Test migrations in a development environment before production

### Security Architecture

FastBase implements a multi-layered security approach:

#### Authentication Flow

1. **Registration**:
   - User submits registration form
   - Password is hashed using bcrypt
   - User record is created in database
   - First user is automatically granted admin privileges

2. **Login**:
   - User submits login credentials
   - System verifies password against stored hash
   - JWT token is generated with user information
   - Token is stored in HTTP-only cookie
   - User is redirected to dashboard

3. **Session Management**:
   - JWT token in cookie is validated on each request
   - Token contains expiration time
   - HTTP-only cookies prevent JavaScript access
   - Secure flag (in production) ensures HTTPS-only transmission

#### Middleware Security Layers

1. **Rate Limiting Middleware** (`app/middleware/rate_limit.py`):
   - Limits requests per IP address
   - Configurable rate and window size
   - Prevents DoS attacks
   - Returns 429 status when limit exceeded

2. **Security Headers Middleware** (`app/middleware/security.py`):
   - Sets Content-Security-Policy
   - Sets X-XSS-Protection
   - Sets X-Frame-Options
   - Sets Strict-Transport-Security
   - Prevents common web vulnerabilities

3. **CSRF Protection** (`app/middleware/csrf.py`):
   - Generates and validates CSRF tokens
   - Protects against cross-site request forgery
   - Required for all non-GET requests

4. **Activity Logger** (`app/middleware/activity_logger.py`):
   - Logs user activities
   - Records IP addresses and timestamps
   - Useful for security auditing

#### Authorization

- Role-based access control (admin vs. regular users)
- Function-level permissions using dependencies
- Template-level conditional rendering based on user role

### Adding New Pages

To add a new page to the application:

1. **Create a route handler** in `app/routes/`:
   ```python
   @router.get("/your-new-page")
   async def your_new_page(
       request: Request,
       db: Session = Depends(get_db)
   ):
       try:
           current_user = await get_current_user_from_cookie(request, db)

           # Your page logic here

           return request.app.state.templates.TemplateResponse(
               "pages/your_new_page.html",
               {
                   "request": request,
                   "user": current_user,
                   # Additional context data
               }
           )
       except:
           # Redirect to login page if not authenticated
           return RedirectResponse(url="/auth/login", status_code=303)
   ```

2. **Create a template** in `app/templates/pages/your_new_page.html`:
   ```html
   {% extends "base.html" %}

   {% block title %}Your Page Title - FastBase{% endblock %}

   {% block content %}
   <div class="container">
       <h1>Your Page Title</h1>
       <!-- Your page content here -->
   </div>
   {% endblock %}
   ```

3. **Add navigation link** in `app/templates/components/sidebar.html`:
   ```html
   <li>
       <a href="/your-new-page" class="{% if request.url.path == '/your-new-page' %}active{% endif %}">
           <i class='bx bx-custom-icon'></i>
           <span>Your Page</span>
       </a>
   </li>
   ```

### Creating Reusable Components

FastBase uses Jinja2 templates for component-based UI development:

1. **Create a component template** in `app/templates/components/`:
   ```html
   <!-- app/templates/components/your_component.html -->
   <div class="your-component">
       <h3>{{ title }}</h3>
       <p>{{ content }}</p>
       <!-- Additional component content -->
   </div>
   ```

2. **Include the component** in your page templates:
   ```html
   {% include "components/your_component.html" with title="Component Title", content="Component content" %}
   ```

3. **For dynamic components**, pass variables from your route handler:
   ```python
   return request.app.state.templates.TemplateResponse(
       "pages/your_page.html",
       {
           "request": request,
           "user": current_user,
           "component_data": {
               "title": "Dynamic Title",
               "content": "Dynamic content"
           }
       }
   )
   ```

   Then in your template:
   ```html
   {% include "components/your_component.html" with title=component_data.title, content=component_data.content %}
   ```

### Project Architecture

FastBase follows a modular architecture:

#### Core Components

1. **Models** (`app/models/`):
   - SQLAlchemy ORM models
   - Define database schema
   - Relationships between entities

2. **Routes** (`app/routes/`):
   - FastAPI route handlers
   - HTTP endpoint definitions
   - Request validation

3. **Services** (`app/services/`):
   - Business logic
   - Database operations
   - Separated from route handlers for better testing

4. **Templates** (`app/templates/`):
   - Jinja2 HTML templates
   - Reusable components
   - Layout definitions

5. **Middleware** (`app/middleware/`):
   - Request/response processing
   - Cross-cutting concerns
   - Security features

#### Data Flow

1. Request → Middleware → Route Handler → Service → Database
2. Database → Service → Route Handler → Template → Response

#### Dependency Injection

FastBase uses FastAPI's dependency injection system:

```python
@router.get("/example")
async def example(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    # Use dependencies here
```

This pattern allows for:
- Clean separation of concerns
- Easier testing
- Automatic documentation
- Reusable components

## Customizing the Template

This template is designed to be a starting point for your web applications. Here are some ways to customize it:

1. **Configuration**: Update the settings in `.env` file
2. **Database Models**: Add or modify models in the `app/models` directory
3. **Routes**: Add new routes in the `app/routes` directory
4. **Templates**: Customize the HTML templates in the `app/templates` directory
5. **Static Files**: Add your CSS, JavaScript, and images in the `app/static` directory

## Admin Account

The first user registered in the system will automatically be granted admin privileges. This admin user can then create additional admin accounts through the admin dashboard.

### Admin Features

- **Admin Dashboard**: Access at `/admin/dashboard`
- **User Management**: View and manage all users
- **Activity Monitoring**: View user activity logs
- **Admin Creation**: Create additional admin users

## UI Components

FastBase includes a variety of pre-built UI components that you can use in your application:

### Available Components

1. **Navigation**:
   - Collapsible sidebar (`app/templates/components/sidebar.html`)
   - Top navbar (`app/templates/components/navbar.html`)
   - Breadcrumbs (`app/templates/components/breadcrumbs.html`)

2. **Forms**:
   - Input fields with validation
   - Dropdowns and select menus
   - Checkboxes and radio buttons
   - File upload controls

3. **Feedback**:
   - Alert messages
   - Toast notifications
   - Progress indicators
   - Loading spinners

4. **Layout**:
   - Grid system
   - Cards and panels
   - Tabs and accordions
   - Modal dialogs

5. **Data Display**:
   - Tables with sorting and pagination
   - Charts and graphs
   - Badges and labels
   - Icons (using Boxicons)

### Using UI Components

Most components can be included in your templates using Jinja's include directive:

```html
{% include "components/alert.html" with type="success", message="Operation completed successfully" %}
```

For more complex components, you can use macros:

```html
{% from "components/forms.html" import input_field %}
{{ input_field(name="username", label="Username", value=user.username, required=true) }}
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify PostgreSQL is running
   - Check connection string in `.env` file
   - Ensure database user has proper permissions

2. **Missing Tables**:
   - Run Alembic migrations: `alembic upgrade head`
   - Check migration scripts for errors
   - Verify models are properly defined

3. **Authentication Issues**:
   - Clear browser cookies
   - Check JWT secret key in `.env`
   - Verify user credentials in database

4. **Template Rendering Problems**:
   - Check for syntax errors in Jinja templates
   - Verify context variables are being passed correctly
   - Look for missing template files

5. **Static Files Not Loading**:
   - Check file paths and URLs
   - Verify static files middleware is configured
   - Clear browser cache

### Debugging Tips

1. **Enable Debug Mode**:
   - Set `DEBUG=True` in `.env`
   - Check detailed error messages

2. **Check Logs**:
   - Application logs for server-side issues
   - Browser console for client-side errors

3. **Use FastAPI's Interactive Docs**:
   - Access `/docs` endpoint for API testing
   - Verify API endpoints are working correctly

4. **Database Inspection**:
   - Use a tool like pgAdmin to inspect the database
   - Verify table schemas match your models

## Security Features

This template includes several security features:

1. **Rate Limiting**: Protection against DoS attacks by limiting the number of requests from a single IP
2. **Security Headers**: Includes various security headers to protect against common web vulnerabilities
3. **CSRF Protection**: Prevents cross-site request forgery attacks
4. **Activity Logging**: Tracks user activities for security auditing
5. **Secure Authentication**: Uses JWT tokens with secure HTTP-only cookies
6. **Password Hashing**: Securely stores passwords using bcrypt
7. **Input Validation**: Validates all user inputs to prevent injection attacks
8. **Error Handling**: Custom error pages that don't leak sensitive information

## License

MIT
