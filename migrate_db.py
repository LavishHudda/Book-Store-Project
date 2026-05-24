import sqlite3

def migrate():
    conn = sqlite3.connect('bookstore.db')
    cursor = conn.cursor()
    
    # 1. Rename existing table
    print("Renaming old books table...")
    cursor.execute('ALTER TABLE books RENAME TO books_old')
    
    # 2. Create new table with correct schema
    print("Creating new books table...")
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Copy data from old table to new table
    # Mapping old columns: id, title, author, price, stock, category
    # to new columns: id, title, author, isbn (null), price, stock, category, added_date (default)
    print("Migrating data...")
    cursor.execute('''
        INSERT INTO books (id, title, author, price, stock, category)
        SELECT id, title, author, price, stock, category FROM books_old
    ''')
    
    # 4. Drop old table
    print("Cleaning up...")
    cursor.execute('DROP TABLE books_old')
    
    conn.commit()
    conn.close()
    print("Database schema successfully upgraded!")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Error during migration: {e}")
