#!/bin/bash
# Datenbank initialisieren:
# Stelle sicher, dass eine lokale PostgreSQL-Datenbank läuft und konfiguriere die Verbindungsdetails in der database.py Datei.
echo "Initialisiere die Datenbank..."
echo "Run 'init' command with `alembic init alembic`, if any errors occur, run 'pip install alembic' first"
# alembic init alembic
echo "Running `alembic upgrade head`..."

alembic upgrade head

# Anwendung starten:
echo "Starte die Anwendung..."
echo "Running `uvicorn main:app --reload`..."

uvicorn main:app --reload

echo "Setup abgeschlossen."
echo "Die Anwendung ist jetzt unter http://127.0.0.1:8000 verfügbar."

echo "Für Tests:"
echo "Run `pytest`"
echo "Run `pytest --cov=app --cov-report=html`"
echo "Run `pytest -v -s test_database.py` for Database Tests"


# Datenbankmigrationen:
echo "Für Datenbankmigrationen, diese werden mit Alembic verwaltet:"
echo "Neue Migration erstellen: `alembic revision --autogenerate -m`"
echo "Migration anwenden: `alembic upgrade head`"
