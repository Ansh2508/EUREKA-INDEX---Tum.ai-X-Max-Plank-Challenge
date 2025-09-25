# CI/CD Pipeline Documentation

## 🚀 Überblick

Unsere CI/CD Pipeline verhindert, dass fehlerhafter Code deployed wird und stellt sicher, dass alle Änderungen getestet sind.

## 📋 Pipeline-Stufen

### 1. **Pull Request Checks** (`.github/workflows/pr-check.yml`)
Läuft bei jedem Pull Request:
- ✅ Syntax-Validation
- ✅ Import-Tests  
- ✅ Basic API-Tests
- ✅ Automatischer PR-Kommentar mit Ergebnissen

### 2. **Vollständige CI/CD** (`.github/workflows/ci-cd.yml`)
Läuft bei Push auf `main` und `develop`:

**Test-Phase:**
- ✅ Multi-Python-Version Testing (3.11, 3.12)
- ✅ Dependency-Caching für schnellere Builds
- ✅ Flake8 Linting
- ✅ Import-Validation
- ✅ Unit Tests mit pytest
- ✅ API Endpoint Tests

**Security-Phase:**
- ✅ Dependency-Vulnerability Checks mit `safety`
- ✅ Code Security Scanning mit `bandit`
- ✅ Security-Report Generation

**Deployment-Check-Phase:**
- ✅ Railway Deployment Simulation
- ✅ Application Startup Test
- ✅ Health Check Validation
- ✅ Integration Tests
- ✅ Deployment Summary Report

## 🛠️ Lokale Entwicklung

### Vor dem Commit testen:
```bash
python run_tests.py
```

### Mit pytest (wenn installiert):
```bash
pip install pytest pytest-asyncio httpx
python -m pytest tests/ -v
```

### Einzelne Tests:
```bash
python -m pytest tests/test_api.py::test_health_check -v
```

## 📁 Test-Struktur

```
tests/
├── __init__.py
├── test_api.py          # API Endpoint Tests
└── test_integration.py  # Integration Tests
```

## 🔒 Deployment Protection

**Railway deployed nur wenn:**
1. ✅ Alle Tests bestehen
2. ✅ Security Checks erfolgreich
3. ✅ Application startet korrekt
4. ✅ Health Check funktioniert

## 🚨 Was passiert bei Fehlern?

- **Test Failures**: Deployment wird blockiert
- **Security Issues**: Builds schlagen fehl
- **Lint Errors**: Warnings, aber kein Build-Stopp
- **Import Errors**: Sofortiger Build-Stopp

## 📊 Status Badges

Nach dem ersten Commit kannst du folgende Badges in die README einfügen:

```markdown
![CI/CD](https://github.com/USERNAME/REPO/workflows/CI%2FCD%20Pipeline/badge.svg)
![PR Checks](https://github.com/USERNAME/REPO/workflows/Pull%20Request%20Checks/badge.svg)
```

## 🔧 Konfiguration

### Python-Versionen ändern:
```yaml
# .github/workflows/ci-cd.yml
strategy:
  matrix:
    python-version: [3.11, 3.12]  # Füge/entferne Versionen
```

### Tests hinzufügen:
1. Neue Datei in `tests/` erstellen
2. Funktionen mit `test_` Prefix
3. Pipeline läuft automatisch

### Dependencies aktualisieren:
- Bearbeite `requirements-minimal.txt`
- Pipeline testet automatisch neue Abhängigkeiten

## 🎯 Best Practices

1. **Kleine, häufige Commits** statt große Änderungen
2. **Pull Requests verwenden** für Code Review
3. **Tests schreiben** vor neuen Features
4. **Lokale Tests** vor Push laufen lassen
5. **Security Warnungen** ernst nehmen

## 🚀 Deployment Flow

```
Developer → Push → GitHub Actions → Tests Pass → Railway Deploy ✅
         ↘ Push → GitHub Actions → Tests Fail → Deployment Blocked ❌
```
