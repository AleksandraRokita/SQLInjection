# Projekt Edukacyjny: Podatności SQL Injection

Niniejsze repozytorium stanowi projekt edukacyjny dotyczący podatności **SQL Injection**, oparty na materiałach, których autorką jest **Aleksandra Rokita**.

## 1. Wprowadzenie i Mechanizm Działania

**Opis ogólny:**
Współczesne aplikacje webowe komunikują się z bazami danych za pomocą zapytań SQL. Błędy w tworzeniu tych zapytań prowadzą do poważnych podatności bezpieczeństwa, z których jedną z najgroźniejszych jest SQL Injection.

**Mechanizm:**
Atak polega na umieszczeniu przez użytkownika specjalnie przygotowanego fragmentu kodu SQL w polach wejściowych (np. formularze logowania, wyszukiwarki, parametry URL).

**Przyczyny:**
Podatność pojawia się, gdy programista tworzy zapytania łącząc bezpośrednio tekst z danymi od użytkownika. Brak walidacji, brak zapytań parametryzowanych i niewłaściwe filtrowanie powodują, że baza traktuje dane użytkownika jako kod SQL.

## 2. Kategorie Ataków

### In-band SQL Injection (Klasyczne)
Kanał ataku i odbioru danych są takie same. Wyniki pojawiają się bezpośrednio na stronie.
* **Error-based:** Wykorzystuje komunikaty o błędach bazy danych do wyciągnięcia informacji o jej strukturze. Atakujący celowo powoduje błąd.
* **Union-based:** Wykorzystuje operator `UNION`, aby połączyć wyniki oryginalnego zapytania z ukradzionymi danymi. Pozwala pobierać dane z innych tabel.
* **Classic:** Polega na manipulacji zapytaniem SQL poprzez pola wejściowe.

### Out-of-band / OAST
Stosowany, gdy aplikacja nie wyświetla wyników. Atakujący wysyła zapytanie nakazujące bazie "zadzwonić" do zewnętrznego serwera (np. DNS, HTTP) w celu przesłania danych.

### Inferential / Blind SQL Injection (Ślepe)
Atakujący nie widzi danych na ekranie. Musi "zgadywać" zadając bazie pytania typu prawda/fałsz.
* **Boolean-based:** Weryfikuje zachowanie strony – normalne załadowanie oznacza "TAK", błąd lub inna treść to "NIE".
* **Time-based:** Atakujący nakazuje bazie opóźnić odpowiedź (np. `SLEEP(5)`) przy spełnieniu warunku. Dłuższe ładowanie strony potwierdza odpowiedź.

## 3. Przykłady Ataków

**Ominięcie logowania:**
Użycie spreparowanej wartości zamyka oczekiwany ciąg znaków, a resztę zapytania (sprawdzanie hasła) zamienia w komentarz, co pozwala na zalogowanie bez hasła.
```sql
admin' --
```

**Atak Union:**
Wstrzyknięcie zapytania `UNION` do wyszukiwarki pozwala odczytać ukryte flagi z tabeli secrets. Testowanie ilości kolumn odbywa się za pomocą `ORDER BY`.
```sql
UNION SELECT 1, flag, 3 FROM secrets --
```

**Atak Error-based:**
Wywołanie błędu zwraca komunikat informujący, że tabele nie mają tej samej liczby kolumn (`SELECTs to the left and right of UNION do not have the same number of result columns`), co zdradza ich strukturę.
```sql
1 UNION SELECT 1,2,3,4
```

**Atak Boolean-based Blind:**
Testowanie logiki True/False poprzez dodanie warunku (strona działa normalnie/prawda) oraz fałszywego warunku (strona wyświetla brak danych/fałsz).
```sql
1 AND 1=1
1 AND 1=2
```

## 4. Metody Zabezpieczania

* **Parametryzacja poleceń (Parameterized Queries):** Najskuteczniejsza metoda. Zamiast sklejać zapytanie, definiuje się zmienne zastępcze. Baza traktuje przekazane wartości ściśle jako dane, a nie kod.
* **Hardening bazy danych:** Stosowanie zasady najmniejszych uprawnień (np. brak konta root dla aplikacji), wyłączanie niepotrzebnych funkcji (np. `xp_cmdshell`) i aktualizowanie silnika bazy.
* **Procedury składowane (Stored Procedures):** Logika jest prekompilowana na serwerze. Chroni podobnie jak parametryzacja i pozwala na radykalne ograniczenie uprawnień dla aplikacji webowej.
* **Mechanizmy ORM:** Użycie narzędzi takich jak Entity Framework Core. ORM automatycznie generuje bezpieczne, sparametryzowane zapytania do bazy, zmniejszając ryzyko błędu programisty.
* **Walidacja danych wejściowych (Input Validation):** Pierwsza linia obrony. Sprawdzanie informacji wejściowych w oparciu o "białe listy" (allow-lists) – np. czy email ma poprawny format.
"# SQLInjection" 
