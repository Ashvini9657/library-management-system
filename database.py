import mysql.connector


MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
DB_NAME = "library_db"


def get_server_connection():
    """Connect to MySQL server (without specifying database)."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

def create_database():
    """Create the database if it doesn't exist."""
    conn = get_server_connection()
    c = conn.cursor()
    c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()
    conn.close()

def get_connection():
    """Connect directly to the library database."""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DB_NAME
    )

def create_tables():
    """Create tables if they don't exist."""
    create_database()  # make sure DB exists first
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    author VARCHAR(255),
                    year INT,
                    status VARCHAR(50)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS members (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS issued_books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_id INT,
                    member_id INT,
                    issue_date DATE,
                    return_date DATE,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )''')

    conn.commit()
    conn.close()
