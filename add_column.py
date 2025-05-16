import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to the fastbase database
conn = psycopg2.connect(
    dbname="fastbase",
    user="postgres",
    password="local",  # Use the password from your DATABASE_URL
    host="localhost",
    port="5432"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cursor = conn.cursor()

# Check if is_admin column exists
cursor.execute("""
SELECT 1
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'is_admin'
""")
exists = cursor.fetchone()

if not exists:
    print("Adding is_admin column to users table...")
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
    print("Column added successfully!")
else:
    print("Column is_admin already exists in users table.")

# Close the connection
cursor.close()
conn.close()
