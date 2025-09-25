# Environment Configuration

## NODE_ENV Support

Die App unterstützt jetzt environment-basierte Konfiguration für Production vs Development.

## 🌍 Environment Variablen

### NODE_ENV
- **`development`** (default): Debug-Modus aktiv
- **`production`**: Optimiert für Production

```bash
# Local Development (Debug-Modus)
NODE_ENV=development

# Production (Clean, optimiert)
NODE_ENV=production
```

## 🔍 Debug vs Production Verhalten

### Development Mode (NODE_ENV=development)
- ✅ **Console Logs**: Alle Debug-Informationen sichtbar
- ✅ **API Docs**: `/docs` und `/redoc` verfügbar
- ✅ **Fehler-Details**: Ausführliche Error-Messages
- ✅ **Debug-Indicator**: Rotes "DEBUG MODE" Banner im Frontend
- ✅ **Import Warnings**: Warnung bei fehlenden Dependencies

### Production Mode (NODE_ENV=production)
- ❌ **Console Logs**: Nur kritische Fehler
- ❌ **API Docs**: `/docs` und `/redoc` deaktiviert
- ❌ **Debug-Output**: Saubere, professionelle Logs
- ❌ **Debug-Indicator**: Kein Banner im Frontend
- ❌ **Import Warnings**: Stumm bei fehlenden Dependencies

## 🚀 Frontend Features

### Debug Logging
```javascript
debugLog('Only shown in development')    // Konditionsabhängig
errorLog('Always shown')                 // Immer sichtbar
infoLog('Always shown')                  // Immer sichtbar
```

### Config API
Das Frontend lädt automatisch die Konfiguration:
```javascript
GET /config
{
  "environment": "production",
  "debug": false,
  "production": true,
  "features": {
    "enhanced_agents": false,
    "api_docs": false
  }
}
```

## 🛠️ Lokale Entwicklung

```bash
# Debug-Modus (default)
uvicorn main:app --reload

# Production-Test lokal
NODE_ENV=production uvicorn main:app --reload
```

## 🚀 Railway Deployment

Railway ist automatisch auf `NODE_ENV=production` konfiguriert in `railway.toml`:

```toml
[deploy.env]
NODE_ENV = "production"
```

## 🎯 Vorteile

- **Saubere Production**: Keine Debug-Ausgaben in Production
- **Bessere Security**: API-Docs nur in Development
- **Performance**: Weniger Logging in Production
- **Developer Experience**: Umfassende Debug-Infos in Development
- **Professional**: Production-Frontend ohne Debug-Banner
