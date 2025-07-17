import sqlite3
from datetime import datetime
import calendar

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect('pharmacare.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support
    return conn

def init_db():
    """Initializes the database by creating required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'User')),
            created_at TEXT NOT NULL
        )
    ''')

    # Create MedicalItems table with image_path
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            unit_price REAL NOT NULL,
            cost_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
            image_path TEXT,
            added_at TEXT NOT NULL
        )
    ''')

    # Create Purchases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity_purchased INTEGER NOT NULL CHECK(quantity_purchased > 0),
            cost_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES medical_items(item_id) ON DELETE RESTRICT
        )
    ''')

    # Create Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL CHECK(quantity_sold > 0),
            sale_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES medical_items(item_id) ON DELETE RESTRICT
        )
    ''')

    # Insert default admin user if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, created_at)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin', 'Admin', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

def add_user(username, password, role):
    """Adds a new user to the users table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO users (username, password, role, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, password, role, created_at))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"User creation failed: {e}")
    finally:
        conn.close()

def authenticate_user(username, password, role):
    """Authenticates a user and returns their details if valid."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ? AND role = ?
    ''', (username, password, role))
    user = cursor.fetchone()
    conn.close()
    return user

def add_item(name, category, unit_price, cost_price, stock_quantity, image_path=None, description=None):
    """Adds a new item to the medical_items table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('''
            INSERT INTO medical_items (name, category, unit_price, cost_price, stock_quantity, image_path, description, added_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, unit_price, cost_price, stock_quantity, image_path, description, added_at))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"Item creation failed: {e}")
    finally:
        conn.close()

def update_item(item_id, name, category, unit_price, cost_price, stock_quantity, image_path=None, description=None):
    """Updates an existing item in the medical_items table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE medical_items
            SET name = ?, category = ?, unit_price = ?, cost_price = ?, stock_quantity = ?, image_path = ?, description = ?
            WHERE item_id = ?
        ''', (name, category, unit_price, cost_price, stock_quantity, image_path, description, item_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"Item update failed: {e}")
    finally:
        conn.close()

def delete_item(item_id):
    """Deletes an item from the medical_items table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM medical_items WHERE item_id = ?', (item_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"Cannot delete item: {e}")
    finally:
        conn.close()

def record_purchase(item_id, quantity, cost_price):
    """Records a purchase and updates item stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('''
            INSERT INTO purchases (item_id, quantity_purchased, cost_price, purchase_date)
            VALUES (?, ?, ?, ?)
        ''', (item_id, quantity, cost_price, purchase_date))
        cursor.execute('''
            UPDATE medical_items SET stock_quantity = stock_quantity + ? WHERE item_id = ?
        ''', (quantity, item_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"Purchase recording failed: {e}")
    finally:
        conn.close()

def record_sale(item_id, quantity, sale_price):
    """Records a sale and updates item stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('SELECT stock_quantity FROM medical_items WHERE item_id = ?', (item_id,))
        stock = cursor.fetchone()
        if not stock or stock['stock_quantity'] < quantity:
            raise Exception("Insufficient stock for sale")

        cursor.execute('''
            INSERT INTO sales (item_id, quantity_sold, sale_price, sale_date)
            VALUES (?, ?, ?, ?)
        ''', (item_id, quantity, sale_price, sale_date))
        cursor.execute('''
            UPDATE medical_items SET stock_quantity = stock_quantity - ? WHERE item_id = ?
        ''', (quantity, item_id))
        conn.commit()
    except (sqlite3.IntegrityError, Exception) as e:
        raise Exception(f"Sale recording failed: {e}")
    finally:
        conn.close()


def search_items(search_term, search_by='name'):
    """Searches items by name, ID, or category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f'SELECT item_id, name, category, unit_price, cost_price, stock_quantity, image_path, description, added_at FROM medical_items WHERE {search_by} LIKE ?'
    cursor.execute(query, (f'%{search_term}%',))
    items = cursor.fetchall()
    conn.close()
    return items

def generate_report(report_type, start_date, end_date):
    """Generates reports for stock, sales, purchases, or profit."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if report_type == 'stock':
        cursor.execute('SELECT item_id, name, category, stock_quantity, image_path FROM medical_items')
        return cursor.fetchall()

    # Extend date range to include full day time
    start_datetime = f"{start_date} 00:00:00"
    end_datetime = f"{end_date} 23:59:59"

    if report_type == 'sales':
        cursor.execute('''
            SELECT s.sale_id, s.item_id, m.name, s.quantity_sold, s.sale_price, s.sale_date
            FROM sales s
            JOIN medical_items m ON s.item_id = m.item_id
            WHERE s.sale_date BETWEEN ? AND ?
        ''', (start_datetime, end_datetime))
        return cursor.fetchall()

    elif report_type == 'purchases':
        cursor.execute('''
            SELECT p.purchase_id, p.item_id, m.name, p.quantity_purchased, p.cost_price, p.purchase_date
            FROM purchases p
            JOIN medical_items m ON p.item_id = m.item_id
            WHERE p.purchase_date BETWEEN ? AND ?
        ''', (start_datetime, end_datetime))
        return cursor.fetchall()

    elif report_type == 'profit':
        cursor.execute('''
            SELECT s.item_id, s.quantity_sold, s.sale_price, m.cost_price, m.unit_price
            FROM sales s
            JOIN medical_items m ON s.item_id = m.item_id
            WHERE s.sale_date BETWEEN ? AND ?
        ''', (start_datetime, end_datetime))
        sales = cursor.fetchall()

        cursor.execute('''
            SELECT p.item_id, p.quantity_purchased, p.cost_price, m.unit_price
            FROM purchases p
            JOIN medical_items m ON p.item_id = m.item_id
            WHERE p.purchase_date BETWEEN ? AND ?
        ''', (start_datetime, end_datetime))
        purchases = cursor.fetchall()

        sales_profit = sum(
            (row['sale_price'] * row['quantity_sold']) - (row['unit_price'] * row['quantity_sold']) for row in sales
        )

        purchase_profit = sum(
            (row['unit_price'] * row['quantity_purchased']) - (row['cost_price'] * row['quantity_purchased']) for row in purchases
        )

        total_profit = sales_profit + purchase_profit

        conn.close()
        return {
            'sales_profit': sales_profit,
            'purchase_profit': purchase_profit,
            'total_profit': total_profit
        }

    conn.close()
    return []


if __name__ == '__main__':
    init_db()