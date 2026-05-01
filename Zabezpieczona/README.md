# SQL Injection: Aplikacja "CorpNet"

### Szczegóły wprowadzonych zabezpieczeń dla poszczególnych modułów:

#### 1. Portal Pracowniczy - Authentication Bypass
**Problem:** Aplikacja wstawiała login i hasło bezpośrednio do ciągu znaków zapytania SQL, pozwalając na ucięcie zapytania znakiem `'` i zignorowanie warunku hasła.
**Rozwiązanie (app.py, endpoint `/login`):**
```python
# PODATNOŚĆ (Przed):
# query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# cursor.execute(query)

# ZABEZPIECZENIE (Po):
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

#### 2. Katalog Produktów - UNION-Based SQL Injection
**Problem:** Wartość parametru wyszukiwarki (klauzula `LIKE`) wklejana była do zapytania, co umożliwiało dopisanie słowa `UNION SELECT` i "wyprowadzenie" dowolnych danych z innej tabeli na ekran aplikacji.
**Rozwiązanie (app.py, endpoint `/search`):**
```python
# PODATNOŚĆ (Przed):
# executed_query = f"SELECT name, description, price FROM products WHERE name LIKE '%{query_param}%'"
# cursor.execute(executed_query)

# ZABEZPIECZENIE (Po) - Znaki % dodajemy do wartości parametru (w krotce), a nie do zapytania SQL:
executed_query = "SELECT name, description, price FROM products WHERE name LIKE ?"
cursor.execute(executed_query, ('%' + query_param + '%',))
```

#### 3. Katalog Pracowników - Error-Based SQL Injection
**Problem:** Zmienna wklejana prosto do zapytania. Wektor ataku oparty na wymuszaniu wyjątków po stronie bazy, w celu wydobywania z niej informacji.
**Rozwiązanie (app.py, endpoint `/user_details`):**
```python
# PODATNOŚĆ (Przed):
# executed_query = f"SELECT id, username, is_admin FROM users WHERE id = {user_id}"
# cursor.execute(executed_query)

# ZABEZPIECZENIE (Po):
executed_query = "SELECT id, username, is_admin FROM users WHERE id = ?"
cursor.execute(executed_query, (user_id,))
```

#### 4. Weryfikacja Statusu Konta - Boolean-Based Blind SQL Injection
**Problem:** Aplikacja podatna na wstrzykiwanie logiki boolowskiej (np. `AND 1=1`), co pozwalało krok po kroku odgadywać wartości przechowywane w bazie bez ich bezpośredniego wyświetlania na ekranie.
**Rozwiązanie (app.py, endpoint `/profile`):**
```python
# PODATNOŚĆ (Przed):
# executed_query = f"SELECT id FROM users WHERE id = {user_id}"
# cursor.execute(executed_query)

# ZABEZPIECZENIE (Po):
executed_query = "SELECT id FROM users WHERE id = ?"
cursor.execute(executed_query, (user_id,))
```

**Podsumowanie:** Zastosowanie parametrów (symbol `?` dla modułu `sqlite3` w języku Python) całkowicie uodporniło kod. Zdejmuje to z programisty obowiązek pisania własnych filtrów znaków (np. blokujących apostrofy), gdyż silnik sam bezpiecznie oddziela treść zapytania od przekazanych wartości. Warto również w przyszłości rozważyć użycie systemów ORM (np. SQLAlchemy) jako kolejnej warstwy abstrakcji zapewniającej domyślne bezpieczeństwo "od razu po wyjęciu z pudełka", a także wdrażać restrykcyjną walidację danych wejściowych.
