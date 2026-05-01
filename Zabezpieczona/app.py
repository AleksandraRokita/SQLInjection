from flask import Flask, request, render_template, g
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

# 1. Authentication Bypass (Classic SQLi)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    user = None
    query = ""
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        db = get_db()
        cursor = db.cursor()
        
        # ZABEZPIECZENIE: Użycie zapytań parametryzowanych (Parameterized Queries)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        
        try:
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            if not user:
                error = "Nieprawidłowa nazwa użytkownika lub hasło."
        except sqlite3.Error as e:
            error = f"Błąd bazy danych: {e}"

    return render_template('login.html', user=user, error=error, query=query)

# 2. UNION-Based SQLi
@app.route('/search')
def search():
    query_param = request.args.get('q', '')
    results = []
    executed_query = ""
    
    if query_param:
        db = get_db()
        cursor = db.cursor()
        
        # ZABEZPIECZENIE: Użycie zapytań parametryzowanych
        executed_query = "SELECT name, description, price FROM products WHERE name LIKE ?"
        
        try:
            cursor.execute(executed_query, ('%' + query_param + '%',))
            results = cursor.fetchall()
        except sqlite3.Error as e:
            # W UNION-based zazwyczaj chcemy ukryć dokładne błędy, by wymusić poprawne zgadnięcie struktury przez atakującego
            pass 
            
    return render_template('search.html', results=results, query=query_param, executed_query=executed_query)

# 3. Error-Based SQLi
@app.route('/user_details')
def user_details():
    user_id = request.args.get('id', '')
    user = None
    error_msg = None
    executed_query = ""
    
    if user_id:
        db = get_db()
        cursor = db.cursor()
        
        # ZABEZPIECZENIE: Użycie zapytań parametryzowanych
        executed_query = "SELECT id, username, is_admin FROM users WHERE id = ?"
        
        try:
            cursor.execute(executed_query, (user_id,))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            # CELOWE ZWRACANIE BŁĘDU DO UŻYTKOWNIKA (Error-Based)
            error_msg = str(e)
            
    return render_template('error_sqli.html', user=user, error=error_msg, executed_query=executed_query)

# 4. Boolean-Based Blind SQLi
@app.route('/profile')
def profile():
    user_id = request.args.get('id', '')
    user_exists = False
    executed_query = ""
    
    if user_id:
        db = get_db()
        cursor = db.cursor()
        
        # ZABEZPIECZENIE: Użycie zapytań parametryzowanych
        executed_query = "SELECT id FROM users WHERE id = ?"
        
        try:
            cursor.execute(executed_query, (user_id,))
            result = cursor.fetchone()
            if result:
                user_exists = True
        except sqlite3.Error as e:
            # Aplikacja ignoruje błędy bazodanowe - widoczny jest tylko efekt "Istnieje" / "Nie istnieje"
            pass
            
    return render_template('profile.html', user_exists=user_exists, id_param=user_id)

if __name__ == '__main__':
    # Upewniamy się, że baza istnieje. Jeśli nie - tworzymy ją na starcie.
    if not os.path.exists(DATABASE):
        import init_db
        init_db.init_db()
        
    print("[*] Laboratorium SQL Injection uruchomione!")
    print("[*] Dostępne pod adresem: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
