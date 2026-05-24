import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_name="bookstore.db"):
        self.db_name = db_name
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Books Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
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
            # Sales Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')
            conn.commit()

    def add_book(self, title, author, isbn, price, stock, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO books (title, author, isbn, price, stock, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, author, isbn, price, stock, category))
            conn.commit()

    def record_sale(self, book_id, quantity):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get book price
            cursor.execute("SELECT price, stock, title FROM books WHERE id = ?", (int(book_id),))
            book = cursor.fetchone()
            if not book:
                return False, "Book not found"
            
            price, current_stock, title = book
            if current_stock < quantity:
                return False, f"Insufficient stock for '{title}'"
            
            total_price = price * quantity
            
            # Record Sale
            cursor.execute('''
                INSERT INTO sales (book_id, quantity, total_price)
                VALUES (?, ?, ?)
            ''', (book_id, quantity, total_price))
            
            # Update Stock
            cursor.execute("UPDATE books SET stock = stock - ? WHERE id = ?", (quantity, book_id))
            
            conn.commit()
            return True, f"Sold {quantity} units of '{title}'"

    def get_sales_report(self):
        query = '''
            SELECT s.id, b.title, s.quantity, s.total_price, s.sale_date 
            FROM sales s 
            JOIN books b ON s.book_id = b.id
            ORDER BY s.sale_date DESC
        '''
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_revenue_by_category(self):
        query = '''
            SELECT b.category, SUM(s.total_price) as revenue
            FROM sales s
            JOIN books b ON s.book_id = b.id
            GROUP BY b.category
        '''
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_top_selling_books(self, limit=5):
        query = '''
            SELECT b.title, SUM(s.quantity) as total_sold
            FROM sales s
            JOIN books b ON s.book_id = b.id
            GROUP BY b.id
            ORDER BY total_sold DESC
            LIMIT ?
        '''
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_all_books(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM books", conn)

    def update_stock(self, book_id, new_stock):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET stock = ? WHERE id = ?", (new_stock, int(book_id)))
            conn.commit()

    def delete_book(self, book_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (int(book_id),))
            conn.commit()

    def get_low_stock_books(self, threshold=5):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM books WHERE stock <= ?", conn, params=(threshold,))

    def search_books(self, query):
        with self.get_connection() as conn:
            query = f"%{query}%"
            return pd.read_sql_query("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ?", 
                                     conn, params=(query, query, query, query))
