# db2.py
import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY,
        manufacture TEXT,
        model TEXT,
        specification TEXT,
        kilometers INTEGER,
        gear_type TEXT,
        fuel TEXT,
        license_plate TEXT,
        price REAL,
        color TEXT,
        extra_items TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spare_parts (
        id INTEGER PRIMARY KEY,
        car_id INTEGER,
        part_name TEXT,
        cost REAL,
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        car_id INTEGER,
        manufacture TEXT,
        model TEXT,
        specification TEXT,
        license_plate TEXT,
        sale_price REAL,
        sale_cost REAL,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    conn.commit()
    conn.close()

def add_car(manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO cars (manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items))
    conn.commit()
    conn.close()

def get_all_cars():
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    conn.close()
    return cars

def get_car_by_id(car_id):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars WHERE id=?", (car_id,))
    car = cursor.fetchone()
    conn.close()
    return car

def update_car(car_id, manufacture, model, specification, kilometers, gear_type, fuel, price, color, extra_items):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE cars
    SET manufacture=?, model=?, specification=?, kilometers=?, gear_type=?, fuel=?, price=?, color=?, extra_items=?
    WHERE id=?''', (manufacture, model, specification, kilometers, gear_type, fuel, price, color, extra_items, car_id))
    conn.commit()
    conn.close()

def delete_car(car_id):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cars WHERE id=?", (car_id,))
    conn.commit()
    conn.close()

def add_spare_part(car_id, part_name, cost):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO spare_parts (car_id, part_name, cost)
    VALUES (?, ?, ?)''', (car_id, part_name, cost))
    conn.commit()
    conn.close()

def delete_spare_part(car_id):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spare_parts WHERE car_id=?", (car_id,))
    conn.commit()
    conn.close()

def get_spare_parts_cost(car_id):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cost) FROM spare_parts WHERE car_id=?", (car_id,))
    cost = cursor.fetchone()[0]
    conn.close()
    return cost if cost else 0.0

def get_spare_parts_by_id(car_id):
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spare_parts WHERE car_id=?", (car_id,))
    car = cursor.fetchone()
    conn.close()
    return car

def get_car_with_spare_parts():
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.id, c.manufacture, c.model, c.specification, c.kilometers, c.gear_type, c.fuel,
           c.license_plate, c.price, c.color, c.extra_items, IFNULL(SUM(sp.cost), 0) as spare_parts_cost
    FROM cars c
    LEFT JOIN spare_parts sp ON c.id = sp.car_id
    GROUP BY c.id
    ''')
    cars = cursor.fetchall()
    conn.close()
    return cars

def add_sale(car_id, manufacture, model, specification, license_plate, sale_price, sale_cost):
    conn = sqlite3.connect('car_inventory.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (car_id, manufacture, model, specification, license_plate, sale_price, sale_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (car_id, manufacture, model, specification, license_plate, sale_price, sale_cost))
    conn.commit()
    conn.close()

def get_sales_data():
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT car_id, sale_price, sale_date FROM sales")
    sales = cursor.fetchall()
    conn.close()
    return sales

def get_all_sales():
    conn = sqlite3.connect("car_inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    conn.close()
    return sales

# Register new user with hashed password
def register_user(username, password):
    conn = sqlite3.connect('car_inventory.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Verify user credentials
def verify_user(username, password):
    conn = sqlite3.connect('car_inventory.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    result = c.fetchone()
    conn.close()
    return result is not None