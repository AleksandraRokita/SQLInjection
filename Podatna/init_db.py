import sqlite3
import os

def init_db():
    db_path = 'database.db'
    
    # Usuwamy starą bazę jeśli istnieje, aby zacząć z czystą kartą
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tworzenie tabeli users
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Tworzenie tabeli products
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Tworzenie tabeli secrets z flagami
    cursor.execute('''
        CREATE TABLE secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag TEXT NOT NULL
        )
    ''')

    # Wypełnianie tabeli users
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'SuperTajneHasloAdmina123!', 1)")
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('jkowalski', 'haslo123', 0)")
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('anowak', 'qwerty', 0)")

    # Wypełnianie tabeli products
    cursor.execute("INSERT INTO products (name, description, price) VALUES ('Laptop PRO', 'Wydajny laptop do pracy z 32GB RAM', 4500.00)")
    cursor.execute("INSERT INTO products (name, description, price) VALUES ('Myszka', 'Myszka bezprzewodowa optyczna', 150.00)")
    cursor.execute("INSERT INTO products (name, description, price) VALUES ('Klawiatura', 'Klawiatura mechaniczna RGB', 400.00)")

    # Wypełnianie tabeli secrets (cel ataku)
    cursor.execute("INSERT INTO secrets (flag) VALUES ('FLAG{SQLi_1s_D4ng3r0us_!}')")
    cursor.execute("INSERT INTO secrets (flag) VALUES ('FLAG{UNION_B4s3d_M4st3r}')")
    cursor.execute("INSERT INTO secrets (flag) VALUES ('FLAG{BLIND_SQLi_N1nj4}')")

    conn.commit()
    conn.close()
    print("Baza danych 'database.db' została pomyślnie utworzona i zainicjowana!")

if __name__ == '__main__':
    init_db()
