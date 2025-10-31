# Railway Deployment Anleitung

## Überblick
Dieses Projekt ist für das Deployment auf Railway mit Railpack/Nixpacks konfiguriert.

## Konfigurierte Dateien

### 1. `requirements.txt` (Root)
Verweist auf die Backend-Requirements, damit Railway Python als Hauptsprache erkennt.

### 2. `nixpacks.toml` (Root)
Fügt Node.js zur Build-Umgebung hinzu:
- Python 3.11 (automatisch erkannt)
- Node.js 20 + npm (manuell hinzugefügt für Frontend-Build)

### 3. `build.sh` (Root)
Build-Script für das gesamte Projekt:
- Installiert Frontend-Dependencies (npm)
- Baut das Frontend (Vite)
- Kopiert die statischen Dateien ins Backend (`backend/static/`)

### 4. `railway.toml` (Root)
Definiert die Railway-Deployment-Konfiguration:
- Builder: Nixpacks
- Build-Befehl: `./build.sh`
- Start-Befehl: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health-Check: `/health` Endpunkt
- Auto-Restart bei Fehlern

### 5. `.railwayignore`
Schließt unnötige Dateien vom Deployment aus (Tests, Dokumentation, etc.)

## Deployment-Schritte

### Option 1: Automatisches Deployment via Git
1. Pushen Sie Ihre Änderungen zu Ihrem Git-Repository
2. Railway wird automatisch den Build-Prozess starten
3. Das Frontend wird gebaut und das Backend gestartet

### Option 2: Railway CLI
```bash
# Railway CLI installieren
npm i -g @railway/cli

# Projekt verlinken
railway link

# Deployment starten
railway up
```

## Erforderliche Umgebungsvariablen

Stellen Sie sicher, dass folgende Umgebungsvariablen in Railway gesetzt sind:

```
# OpenAI / LLM APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key

# Production Flag
NODE_ENV=production

# Optional: Custom Port (Railway setzt $PORT automatisch)
PORT=8000
```

## Health-Check

Railway überprüft automatisch den `/health` Endpunkt:
- URL: `https://your-app.railway.app/health`
- Timeout: 300 Sekunden
- Bei Fehler: Automatischer Neustart

## Logs anzeigen

```bash
# Via Railway CLI
railway logs

# Via Railway Dashboard
https://railway.app/project/your-project-id/service/your-service-id
```

## Troubleshooting

### "No start command was found"
✅ Behoben durch das `start` Script in `package.json`

### "Module not found"
- Überprüfen Sie die `requirements-minimal.txt`
- Stellen Sie sicher, dass alle Dependencies installiert sind

### Build schlägt fehl
- Überprüfen Sie die Build-Logs in Railway
- Stellen Sie sicher, dass `frontend/package.json` korrekt ist
- Überprüfen Sie die Node.js und Python Versionen

### Server startet nicht
- Überprüfen Sie die Umgebungsvariablen
- Überprüfen Sie die Logs: `railway logs`
- Überprüfen Sie den Health-Check-Endpunkt

## Lokales Testen des Production-Builds

```bash
# Build-Script ausführen
chmod +x build.sh
./build.sh

# Backend starten
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Dann öffnen Sie: `http://localhost:8000`

## Wie das Deployment funktioniert

1. **Spracherkennung**: Railway erkennt Python als Hauptsprache (wegen `requirements.txt` im Root)
2. **Zusätzliche Tools**: `nixpacks.toml` fügt Node.js hinzu
3. **Dependency-Installation**: Railway installiert automatisch:
   - Python-Packages aus `requirements.txt`
   - Node.js-Packages aus `frontend/package.json` (via build.sh)
4. **Build-Phase**: `build.sh` baut das Frontend und kopiert die Dateien
5. **Start**: Backend-Server startet und serviert das Frontend

## Support

Bei Problemen:
1. Überprüfen Sie die Railway-Logs
2. Überprüfen Sie die Umgebungsvariablen
3. Testen Sie lokal mit Production-Einstellungen
4. Konsultieren Sie die [Railway Dokumentation](https://docs.railway.app)

