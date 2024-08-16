# SyllabusMatcherAI

SyllabusMatcherAI ist eine FastAPI-Anwendung, die es Universitäten ermöglicht, Lehrveranstaltungen zu vergleichen und Übereinstimmungen zwischen verschiedenen Institutionen zu analysieren. Diese Anwendung ist in Python geschrieben und verwendet PostgreSQL zur Speicherung von Daten.

## Inhaltsverzeichnis

- [Entwicklung](#entwicklung)
  - [Voraussetzungen](#voraussetzungen)
  - [Installation](#installation)
  - [Lokale Entwicklung](#lokale-entwicklung)
  - [Testing](#testing)
- [Deployment](#deployment)
  - [Kubernetes Setup](#kubernetes-setup)
  - [Deployment der Entwicklungsumgebung](#deployment-der-entwicklungsumgebung)
  - [Deployment der Produktionsumgebung](#deployment-der-produktionsumgebung)
- [CI/CD mit GitLab](#cicd-mit-gitlab)
  - [Pipeline Stages](#pipeline-stages)
  - [Datenbankmigrationen](#datenbankmigrationen)
  - [Backup und Wiederherstellung](#backup-und-wiederherstellung)
- [Monitoring und Alerts](#monitoring-und-alerts)
- [Datenbankverwaltung](#datenbankverwaltung)
  - [Automatisierte Backups](#automatisierte-backups)
  - [Manuelle Wiederherstellung](#manuelle-wiederherstellung)
  - [Testen der Backups](#testen-der-backups)
- [Nützliche Befehle](#nützliche-befehle)

## Entwicklung

### Voraussetzungen

- Python 3.9 oder höher
- Docker
- Kubernetes Cluster (für das Deployment)
- GitLab CI/CD (für CI/CD-Pipeline)
- PostgreSQL 13

### Installation


<details>
<summary>Click to expand for an example file structure</summary>

<!-- Include the content of your other .md file here -->
{% include_relative ./example_file_structure.md %}

</details>


1. **Repository klonen:**

   ```bash
   git clone https://gitlab.com/yourusername/syllabusmatcherai.git
   cd syllabusmatcherai
   ```
2.  **Virtuelle Umgebung erstellen und Abhängigkeiten installieren:**
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    

### Lokale Entwicklung

1.  **Datenbank initialisieren:**
    
    Stelle sicher, dass eine lokale PostgreSQL-Datenbank läuft und konfiguriere die Verbindungsdetails in der `database.py` Datei.
    
2.  **Datenbankmigrationen ausführen:**
    
    ```bash
    alembic upgrade head
    ```
    
3.  **Anwendung starten:**
    
    ```bash
    uvicorn main:app --reload
    ```
    
    Die Anwendung ist jetzt unter `http://127.0.0.1:8000` verfügbar.
    

### Testing

1.  **Unit-Tests ausführen:**
    
    ```bash
    pytest
    ```
    
2.  **Datenbank-Tests:**
    
    Teste Datenbankoperationen in einer isolierten Umgebung:
    
    ```bash
    pytest -v -s test_database.py
    ```
    

Deployment
----------

### Kubernetes Setup

1.  **Namespaces erstellen:**
    
    ```bash
    kubectl create namespace syllabusmatcherai-dev
    kubectl create namespace syllabusmatcherai-prod
    ```
    
2.  **Ingress Controller installieren:**
    
    Installiere den NGINX Ingress Controller, falls noch nicht geschehen:
    
    ```bash
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    helm install ingress-nginx ingress-nginx/ingress-nginx
    ```
    

### Deployment der Entwicklungsumgebung

1.  **Deployment und Service bereitstellen:**
    
    ```bash
    kubectl apply -f kubernetes/dev-deployment.yaml
    kubectl apply -f kubernetes/dev-ingress.yaml
    kubectl apply -f kubernetes/postgresql-deployment.yaml
    ```
    
2.  **Anwendung über Ingress zugreifen:**
    
    Die Entwicklungsumgebung ist unter `http://syllabusmatcherai-dev.its.ingress.wu.ac.at` erreichbar.
    

### Deployment der Produktionsumgebung

1.  **Deployment und Service bereitstellen:**
    
    ```bash
    kubectl apply -f kubernetes/prod-deployment.yaml
    kubectl apply -f kubernetes/prod-ingress.yaml
    kubectl apply -f kubernetes/postgresql-deployment.yaml
    ```
    
2.  **Anwendung über Ingress zugreifen:**
    
    Die Produktionsumgebung ist unter `http://syllabusmatcherai.its.ingress.wu.ac.at` erreichbar.
    

CI/CD mit GitLab
----------------

### Pipeline Stages

Die `.gitlab-ci.yml` Datei definiert eine CI/CD-Pipeline mit den folgenden Stages:

*   **Build**: Docker-Image bauen und in die GitLab Container Registry pushen.
*   **Lint**: Code-Qualitätstests mit Flake8, Pylint und Mypy.
*   **Test**: Unit-Tests und Datenbank-Tests ausführen.
*   **Security**: Sicherheitsscans mit Bandit.
*   **Deploy-Dev**: Deployment in der Entwicklungsumgebung.
*   **Deploy-Prod**: Deployment in der Produktionsumgebung.
*   **Migrate**: Datenbankmigrationen ausführen.
*   **Backup-Restore-Test**: Testen von Backups und Wiederherstellung.
*   **API-Test**: End-to-End API-Tests nach dem Deployment.

### Datenbankmigrationen

Migrationen werden mit Alembic verwaltet:

1.  **Neue Migration erstellen:**
    
    ```bash
    alembic revision --autogenerate -m "Beschreibung der Migration"
    ```
    
2.  **Migration anwenden:**
    
    ```bash
    alembic upgrade head
    ```
    

### Backup und Wiederherstellung

1.  **Automatisierte Backups:**
    
    Die PostgreSQL-Datenbank wird täglich um 2 Uhr durch einen Kubernetes CronJob gesichert. Backups werden in einem Persistent Volume gespeichert.
    
2.  **Manuelle Wiederherstellung:**
    
    Ein Kubernetes Job kann verwendet werden, um ein bestimmtes Backup wiederherzustellen.
    
3.  **Testen der Backups:**
    
    Regelmäßige Tests auf den wiederhergestellten Backups werden in der CI/CD-Pipeline durchgeführt.
    

Monitoring und Alerts
---------------------

*   **Prometheus und Grafana**: Verwende Prometheus und Grafana für die Überwachung der Anwendung und der Datenbank.
*   **Alerts**: Konfiguriere Alerts in Grafana, um über Probleme in der Produktionsumgebung benachrichtigt zu werden.

Datenbankverwaltung
-------------------

### Automatisierte Backups

Backups werden durch einen Kubernetes CronJob regelmäßig erstellt. Die Backups werden in einem Persistent Volume (`postgres-backup-pvc`) gespeichert.

### Manuelle Wiederherstellung

Falls eine manuelle Wiederherstellung erforderlich ist, kann der PostgreSQL Restore-Job (`postgres-restore-job.yaml`) verwendet werden.

### Testen der Backups

Automatisierte Tests stellen sicher, dass die Backups funktionsfähig und konsistent sind. Diese Tests werden in der CI/CD-Pipeline integriert und regelmäßig ausgeführt.

Nützliche Befehle
-----------------

*   **Docker-Image lokal bauen:**
    
    ```bash
    docker build -t my-fastapi-app:latest .
    ```
    
*   **Docker-Image in die Registry pushen:**
    
    ```bash
    docker push <your_dockerhub_username>/my-fastapi-app:latest
    ```
    
*   **Datenbankmigrationen generieren:**
    
    ```bash
    alembic revision --autogenerate -m "Neue Migration"
    ```
    
*   **Kubernetes Ressource anwenden:**
    
    ```bash
    kubectl apply -f <ressource.yaml>
    ```
    
*   **Kubernetes Pod Logs anzeigen:**
    
    ```bash
    kubectl logs <pod-name>
    ```
    

Support
-------

Bei Fragen oder Problemen kannst du dich an den Entwickler oder das DevOps-Team wenden.



### Docker-Compose
Ein `docker-compose.yml`\-File ermöglicht es dir, die verschiedenen Dienste, die für dein Projekt notwendig sind, gemeinsam zu orchestrieren. Für das SyllabusMatcherAI-Projekt, das PostgreSQL als Datenbank und FastAPI als Web-Server verwendet, sieht das `docker-compose.yml`\-File folgendermaßen aus:

```yaml

version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: syllabusmatcherai_postgres
    environment:
      POSTGRES_DB: syllabusmatcher
      POSTGRES_USER: syllabus_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - syllabusmatcherai_network

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: syllabusmatcherai_fastapi
    environment:
      DATABASE_URL: postgresql://syllabus_user:your_password@postgres:5432/syllabusmatcher
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    networks:
      - syllabusmatcherai_network

  alembic:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: syllabusmatcherai_alembic
    environment:
      DATABASE_URL: postgresql://syllabus_user:your_password@postgres:5432/syllabusmatcher
    networks:
      - syllabusmatcherai_network
    depends_on:
      - postgres
    entrypoint: >
      /bin/sh -c "alembic upgrade head && exit"

volumes:
  postgres_data:

networks:
  syllabusmatcherai_network:
    driver: bridge
```

### Erklärung der `docker-compose.yml`

*   **Version**: Die Version des Compose-Files, hier `3.8`, eine gängige Version für viele Docker-Compose-Features.
    
*   **Services**:
    
    *   **postgres**:
        
        *   Verwendet das PostgreSQL 13 Image.
        *   Setzt die Datenbank, den Benutzer und das Passwort mit den Umgebungsvariablen `POSTGRES_DB`, `POSTGRES_USER` und `POSTGRES_PASSWORD`.
        *   Die Daten werden in einem Docker-Volume namens `postgres_data` gespeichert, das auf `/var/lib/postgresql/data` gemountet wird.
        *   Der Dienst wird im `syllabusmatcherai_network` Netzwerk betrieben.
    *   **fastapi**:
        
        *   Baut das FastAPI-Docker-Image aus dem aktuellen Kontext (`.`) und verwendet das angegebene `Dockerfile`.
        *   Die `DATABASE_URL`\-Umgebungsvariable stellt die Verbindung zur PostgreSQL-Datenbank her.
        *   Exponiert den Port 8000 auf dem Hostsystem, damit die Anwendung unter `http://localhost:8000` erreichbar ist.
        *   Hängt vom `postgres` Dienst ab, sodass FastAPI erst startet, wenn die Datenbank läuft.
    *   **alembic**:
        
        *   Baut das Alembic-Docker-Image ebenfalls aus dem aktuellen Kontext (`.`).
        *   Die `DATABASE_URL`\-Umgebungsvariable stellt die Verbindung zur PostgreSQL-Datenbank her.
        *   Führt Alembic-Migrationen bei jedem Start des Containers durch und beendet sich dann.
*   **Volumes**:
    
    *   **postgres\_data**: Persistiert die Datenbankdaten auf dem Hostsystem.
*   **Networks**:
    
    *   **syllabusmatcherai\_network**: Ein separates Netzwerk, in dem alle Dienste miteinander kommunizieren können.

### Verwendung

1.  **Starten der Dienste**:
    
    Um alle Dienste zu starten, navigiere in das Verzeichnis, in dem sich das `docker-compose.yml` befindet, und führe den folgenden Befehl aus:
    
    ```bash
    docker-compose up -d
    ```
    
    Dies startet alle definierten Dienste im Hintergrund.
    
2.  **Stoppen der Dienste**:
    
    Um alle Dienste zu stoppen, verwende:
    
    ```bash
    docker-compose down
    ```
    
    Dies stoppt und entfernt alle Container, aber die Daten in `postgres_data` bleiben bestehen.
    
3.  **Logs anzeigen**:
    
    Um die Logs der Dienste zu sehen, benutze:
    
    ```bash
    docker-compose logs -f
    ```
    
    Dies zeigt die Echtzeit-Logs aller Dienste.
    
4.  **Migrationen manuell ausführen**:
    
    Falls du die Migrationen manuell ausführen möchtest, kannst du den Alembic-Container wie folgt starten:
    
    ```bash
    docker-compose run alembic
    ```
    

#### Fazit

Das `docker-compose.yml`\-File ermöglicht es dir, alle notwendigen Komponenten für die SyllabusMatcherAI-Anwendung leicht zu starten und zu verwalten. Es orchestriert die FastAPI-Anwendung, PostgreSQL-Datenbank und führt die notwendigen Datenbankmigrationen durch, alles in einem einzigen Befehl.

### Zusammenfassung

Diese `README.md` bietet eine umfassende Anleitung, die alle Schritte zur Entwicklung, zum Deployment und zur Verwaltung deiner Anwendung abdeckt. Sie enthält Informationen zu:

- **Entwicklung**: Lokale Installation, Testen und Starten der Anwendung.
- **Deployment**: Bereitstellung in Kubernetes sowohl für Entwicklungs- als auch Produktionsumgebungen.
- **CI/CD**: Integration mit GitLab CI/CD, einschließlich Pipelinestages und Datenbankmigrationen.
- **Backup und Wiederherstellung**: Verwaltung und Testen von Datenbank-Backups.
- **Monitoring und Alerts**: Einrichtung von Überwachungs- und Alarmsystemen.

Diese `README.md` sollte es allen Beteiligten ermöglichen, die Anwendung erfolgreich zu entwickeln, zu deployen und zu betreiben.
```