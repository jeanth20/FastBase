import psycopg2

# Connect to the fastbase database
conn = psycopg2.connect(
    dbname="fastbase",
    user="postgres",
    password="local",
    host="localhost",
    port="5432"
)

# Create a cursor
cursor = conn.cursor()

# Check if users table exists
cursor.execute("""
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE  table_schema = 'public'
   AND    table_name   = 'users'
);
""")
users_exists = cursor.fetchone()[0]

# Check if user_activities table exists
cursor.execute("""
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE  table_schema = 'public'
   AND    table_name   = 'user_activities'
);
""")
user_activities_exists = cursor.fetchone()[0]

print(f"Users table exists: {users_exists}")
print(f"User activities table exists: {user_activities_exists}")

# If tables exist, show their structure
if users_exists:
    cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'users';
    """)
    print("\nUsers table structure:")
    for column in cursor.fetchall():
        print(f"  {column[0]}: {column[1]}")

if user_activities_exists:
    cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'user_activities';
    """)
    print("\nUser activities table structure:")
    for column in cursor.fetchall():
        print(f"  {column[0]}: {column[1]}")

# Close the connection
cursor.close()
conn.close()
