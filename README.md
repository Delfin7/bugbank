# 🏦 BugBank - Aplikacja Treningowa dla Testerów Selenium

BugBank to symulator systemu bankowego stworzony specjalnie do nauki automatyzacji testów z wykorzystaniem Selenium
WebDriver. Aplikacja zawiera **celowo zaimplementowane wyzwania**, które testerzy spotykają w rzeczywistych projektach
komercyjnych.

## 🎯 Cel projektu

Aplikacja pozwala przećwiczyć:

- Wszystkie typy lokatorów (ID, Name, CSS, XPath, etc.)
- Obsługę dynamicznych elementów i AJAX
- Waity (implicit, explicit, custom)
- Iframe, alerty, okna/taby
- ActionChains (hover, drag&drop, double-click, context menu)
- Shadow DOM
- Formularze, uploady plików
- I wiele więcej!

## 🚀 Szybki start

### Wymagania

- Python 3.8+
- pip

### Instalacja

```bash
# Klonowanie repozytorium
git clone https://github.com/Delfin7/bugbank.git
cd bugbank

# Utworzenie wirtualnego środowiska (opcjonalne, ale zalecane)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows

# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie aplikacji
python run.py
```

Aplikacja będzie dostępna pod adresem: **http://localhost:5000**

## 👥 Użytkownicy testowi

| Login           | Hasło         | Scenariusz                      |
|-----------------|---------------|---------------------------------|
| `standard_user` | `password123` | Normalne logowanie              |
| `2fa_user`      | `password123` | Wymaga kodu 2FA (kod: `123456`) |
| `locked_user`   | `password123` | Konto zablokowane               |
| `expired_user`  | `password123` | Hasło wygasłe - wymusza zmianę  |
| `empty_user`    | `password123` | Brak kont i transakcji          |
| `rich_user`     | `password123` | Dużo danych (test paginacji)    |

## 🗺️ Mapa aplikacji

```
/login              → Strona logowania
/two-factor         → Weryfikacja 2FA
/dashboard          → Panel główny
/accounts           → Lista kont
/accounts/<id>      → Szczegóły konta
/transfers/new      → Nowy przelew (wizard 3-krokowy)
/cards              → Zarządzanie kartami
/messages           → Skrzynka wiadomości
/settings           → Ustawienia profilu
/regulations        → Regulamin (otwiera się w nowym oknie)
```

## 📁 Struktura projektu

```
bugbank/
├── run.py                 # Punkt wejścia
├── config.py              # Konfiguracja
├── requirements.txt       # Zależności
├── app/
│   ├── __init__.py        # Inicjalizacja Flask
│   ├── models.py          # Modele bazy danych
│   ├── seed_data.py       # Dane testowe
│   ├── routes/            # Endpointy
│   ├── templates/         # Szablony HTML
│   └── static/            # CSS, JS, obrazki
```

## 🔧 Konfiguracja

Aplikacja może działać w różnych trybach:

```bash
# Tryb deweloperski (domyślny)
export FLASK_ENV=development
python run.py

# Tryb produkcyjny
export FLASK_ENV=production
python run.py

# Własny port
python run.py --port 8080
```

## 📝 Licencja

MIT License - używaj dowolnie do celów edukacyjnych.

---

**Uwaga**: Ta aplikacja jest przeznaczona wyłącznie do celów edukacyjnych. Nie używaj jej jako wzorca dla prawdziwych
aplikacji bankowych!
