# API de Inventario y Precios

API RESTful profesional para exponer datos de inventario y precios desde archivos FoxPro DBF.

## 🎯 Características

- ✅ Lectura eficiente de archivos DBF de FoxPro
- ✅ API RESTful con endpoints bien definidos
- ✅ Sistema de caché multinivel (memoria + disco)
- ✅ Respuestas instantáneas (< 100ms)
- ✅ Sincronización automática programable
- ✅ Logging completo y estructurado
- ✅ Manejo robusto de errores
- ✅ Validación y limpieza de datos
- ✅ CORS configurable
- ✅ Health checks
- ✅ Caché persistente entre reinicios
- ✅ Actualización en background sin bloqueos
- ✅ Optimizado para rendimiento
- ✅ Seguridad con API Key

## 📋 Requisitos

- Python 3.8 o superior
- Acceso a los archivos DBF de FoxPro
- Windows (para instalación como servicio)

## 🚀 Instalación Rápida

### Paso 1: Configurar variables de entorno

1. Copiar el archivo de ejemplo:
```bash
copy .env.example .env
```

2. Editar `.env` con tus configuraciones:
```env
DBF_PATH=../DbfRed
API_KEY=tu_clave_secreta_aqui
PORT=5000
SYNC_INTERVAL_MINUTES=30
```

### Paso 2: Instalar como servicio de Windows

1. Ejecutar como ADMINISTRADOR: `instalar_servicio.bat`
2. Ingresar credenciales de Windows cuando se solicite
3. El servicio se instalará y arrancará automáticamente

### Paso 3: Verificar instalación

Abrir en navegador:
```
http://localhost:5000/health
```

## 🌐 Acceso desde Internet (Exponer API al mundo)

Tienes 2 opciones para que cualquier PC del mundo pueda acceder a tu API:

### Opción 1: Port Forwarding en Router (Tiempo real)

Configurar Port Forwarding en tu router para el puerto 8090 → IP local del servidor.

**Ventajas:**
- ✅ API en tiempo real
- ✅ Todos los endpoints disponibles (GET, POST, etc.)

**Desventajas:**
- ❌ Requiere acceso al router
- ❌ Configuración manual

**Guía:** Ver sección "Port Forwarding" más abajo.

---

### Opción 2: Cloudflare R2 (Recomendado si no tienes acceso al router)

Sube automáticamente el inventario a Cloudflare R2 cada 30 minutos.

**Ventajas:**
- ✅ Sin Port Forwarding
- ✅ URL pública permanente
- ✅ HTTPS incluido
- ✅ Gratis (10GB/mes)
- ✅ CDN global (súper rápido)

**Desventajas:**
- ❌ Actualización cada 30 minutos (no tiempo real)
- ❌ Solo lectura (archivos JSON)

**Guía completa:** Ver archivo `GUIA_CLOUDFLARE_R2.md`

**Configuración rápida:**
1. Crear cuenta en cloudflare.com
2. Crear bucket R2
3. Obtener credenciales
4. Configurar en `.env`:
   ```env
   CLOUDFLARE_ENABLED=True
   CLOUDFLARE_ACCOUNT_ID=tu_account_id
   CLOUDFLARE_ACCESS_KEY_ID=tu_access_key
   CLOUDFLARE_SECRET_ACCESS_KEY=tu_secret_key
   CLOUDFLARE_BUCKET_NAME=tu_bucket
   ```
5. Reinstalar dependencias: `.\venv\Scripts\pip.exe install -r requirements.txt`
6. Reiniciar servicio: `sc stop ProductosSyncAPI && sc start ProductosSyncAPI`
7. Acceder a: `https://tu-bucket.r2.dev/inventario.json`

---

### Port Forwarding (Opción 1 - Detalle)

1. Obtener tu IP local:
```bash
ipconfig
```
Busca "IPv4" (ejemplo: 192.168.1.100)

2. Acceder a la configuración de tu router:
   - Abrir navegador: http://192.168.1.1 (o http://192.168.0.1)
   - Usuario/contraseña: admin/admin (o ver etiqueta del router)

3. Configurar Port Forwarding:
   - Buscar sección: "Port Forwarding", "Virtual Server" o "NAT"
   - Crear nueva regla:
     - Puerto externo: 5000
     - Puerto interno: 5000
     - IP interna: 192.168.1.100 (tu IP local)
     - Protocolo: TCP
   - Guardar y aplicar

4. Obtener tu IP pública:
   - Visitar: https://www.whatismyip.com/
   - Anotar la IP (ejemplo: 203.0.113.45)

5. Probar acceso externo:
```
http://203.0.113.45:5000/api/inventario?api_key=tu_clave
```

### Opción 2: Usar ngrok (Más fácil, para pruebas)

1. Descargar ngrok: https://ngrok.com/download
2. Ejecutar:
```bash
ngrok http 5000
```
3. Copiar la URL pública que aparece (ejemplo: https://abc123.ngrok.io)
4. Acceder desde cualquier lugar:
```
https://abc123.ngrok.io/api/inventario?api_key=tu_clave
```

### Opción 3: Usar un dominio (Profesional)

1. Registrar un dominio (ejemplo: miempresa.com)
2. Configurar DNS apuntando a tu IP pública
3. Configurar Port Forwarding en router
4. Opcional: Instalar certificado SSL con Let's Encrypt

## 📡 Endpoints de la API

### Información general
```
GET /
```

### Health Check
```
GET /health
```

### Inventario completo
```
GET /api/inventario
Headers: X-API-Key: tu_clave_aqui
Query params:
  - disponible_solo=true (solo productos con stock)
  - limit=100 (limitar resultados)
```

### Inventario por producto
```
GET /api/inventario/<codigo>
Headers: X-API-Key: tu_clave_aqui
```

### Lista de productos
```
GET /api/productos
Headers: X-API-Key: tu_clave_aqui
Query params:
  - activos_solo=true (default)
  - limit=100
```

### Precios de venta
```
GET /api/precios
Headers: X-API-Key: tu_clave_aqui
Query params:
  - limit=100
```

### Limpiar caché
```
POST /api/cache/clear
Headers: X-API-Key: tu_clave_aqui
```

### Actualizar caché en background
```
POST /api/cache/refresh
Headers: X-API-Key: tu_clave_aqui
```

## 🔐 Seguridad

### Autenticación con API Key

Todas las rutas de la API requieren autenticación. Hay dos formas de enviar la API Key:

1. Header HTTP (recomendado):
```bash
curl -H "X-API-Key: tu_clave_aqui" http://localhost:5000/api/inventario
```

2. Query parameter:
```bash
curl http://localhost:5000/api/inventario?api_key=tu_clave_aqui
```

### Generar API Key segura

En Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

O usar un generador online: https://randomkeygen.com/

## ⚙️ Configuración

### Variables de entorno (.env)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DBF_PATH` | Ruta a los archivos DBF | ../DbfRed |
| `API_KEY` | Clave de autenticación | (requerido) |
| `SYNC_INTERVAL_MINUTES` | Intervalo de sincronización | 30 |
| `PORT` | Puerto del servidor | 5000 |
| `HOST` | Host del servidor | 0.0.0.0 |
| `FLASK_ENV` | Ambiente | production |
| `FLASK_DEBUG` | Modo debug | False |
| `SECRET_KEY` | Clave secreta de Flask | (auto) |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | * |
| `DBF_ENCODING` | Encoding de archivos DBF | latin-1 |
| `CACHE_TIMEOUT` | Timeout de caché (segundos) | 10800 |
| `LOG_LEVEL` | Nivel de logging | INFO |

## 🔧 Arquitectura

```
ProductosSync/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuración centralizada
│   ├── logger.py          # Sistema de logging
│   ├── dbf_reader.py      # Lectura de archivos DBF
│   ├── cache_manager.py   # Gestión de caché
│   ├── api.py             # API Flask
│   └── scheduler.py       # Tareas programadas
├── data/
│   └── cache/             # Caché en disco
├── logs/                  # Archivos de log
├── app.py                 # Punto de entrada
├── requirements.txt       # Dependencias
├── .env                   # Configuración (no versionar)
├── run.bat                # Ejecutar en modo desarrollo
├── instalar_servicio.bat  # Instalar como servicio
└── README.md
```

## 📊 Rendimiento

- Sistema de caché multinivel (memoria + disco)
- Respuestas instantáneas: < 100ms
- Sincronización automática cada 30 minutos (configurable)
- Caché persistente entre reinicios (3 horas de validez)
- Lectura optimizada de archivos DBF
- Actualización en background sin bloqueos
- Rate limiting: 200 requests/minuto por IP

## 🛠️ Gestión del Servicio

### Ver estado
```bash
sc query ProductosSyncAPI
```

### Iniciar servicio
```bash
sc start ProductosSyncAPI
```

### Detener servicio
```bash
sc stop ProductosSyncAPI
```

### Reiniciar servicio
```bash
sc stop ProductosSyncAPI
timeout /t 2
sc start ProductosSyncAPI
```

### Ver logs
```bash
type logs\service_out.log
type logs\app.log
```

### Desinstalar servicio
Ejecutar como ADMINISTRADOR: `desinstalar_servicio.bat`

## 🐛 Troubleshooting

### Error: "Ruta DBF no encontrada"
Verificar que `DBF_PATH` en `.env` apunte correctamente a los archivos DBF.

### Error: "API key requerida"
Asegurarse de incluir el header `X-API-Key` o el parámetro `api_key` en las peticiones.

### El servicio no inicia
1. Verificar logs en `logs/service_err.log`
2. Verificar que las credenciales de Windows sean correctas
3. Verificar que el puerto 5000 no esté en uso

### No puedo acceder desde otro PC
1. Verificar que el firewall permita el puerto 5000
2. Verificar que el servicio esté corriendo: `sc query ProductosSyncAPI`
3. Probar acceso local primero: http://localhost:5000/health
4. Verificar Port Forwarding en router si accedes desde internet

### El caché no se actualiza
Llamar manualmente: `POST /api/cache/refresh` o reiniciar el servicio.

## 📝 Logs

Los logs se guardan en:
- Consola (stdout)
- Archivo: `logs/app.log`
- Servicio: `logs/service_out.log` y `logs/service_err.log`

Niveles de log: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 📄 Licencia

Proyecto privado

## 🤝 Soporte

Para problemas o consultas, revisar los logs en `logs/app.log`.
