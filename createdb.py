import sqlite3

# Database file name
DB_FILE = "school_roll.db"

def create_tables():
    """
    Creates the necessary tables in the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    # Create the grades table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            grade REAL NOT NULL,
            date TEXT NOT NULL,
            pdf_path TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")

def add_sample_data():
    """
    Adds sample data to the database for testing purposes.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()


if __name__ == "__main__":
    print("Creating database...")
    create_tables()
    print("Adding sample data...")
    add_sample_data()
    print(f"Database '{DB_FILE}' is ready!")