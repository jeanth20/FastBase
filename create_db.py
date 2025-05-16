import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="local",
    host="localhost",
    port="5432"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cursor = conn.cursor()

# Check if database exists
cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'fastbase'")
exists = cursor.fetchone()

if not exists:
    print("Creating database 'fastbase'...")
    cursor.execute("CREATE DATABASE fastbase")
    print("Database 'fastbase' created successfully!")
else:
    print("Database 'fastbase' already exists.")

# Close the connection
cursor.close()
conn.close()

print("Now creating tables...")

# Connect to the fastbase database
conn = psycopg2.connect(
    dbname="fastbase",
    user="postgres",
    password="local",
    host="localhost",
    port="5432"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
""")

# Create user_activities table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type VARCHAR(255),
    endpoint VARCHAR(255),
    ip_address VARCHAR(255),
    user_agent VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_user_activities_id ON user_activities (id);
""")

print("Tables created successfully!")

# Close the connection
cursor.close()
conn.close()
