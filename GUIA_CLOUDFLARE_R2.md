# 📘 GUÍA: Configurar Cloudflare R2 para exponer inventario sin Port Forwarding

Esta guía te muestra cómo subir automáticamente tu inventario a Cloudflare R2 para accederlo desde internet **sin necesidad de Port Forwarding**.

---

## 🎯 ¿Qué lograrás?

- ✅ Inventario accesible desde internet sin Port Forwarding
- ✅ URL pública y permanente
- ✅ HTTPS incluido (seguro)
- ✅ Gratis (10GB/mes)
- ✅ Actualización automática cada 30 minutos
- ✅ CDN global (súper rápido)

---

## 📋 PASO 1: Crear cuenta en Cloudflare (Gratis)

1. Ve a: https://dash.cloudflare.com/sign-up
2. Crea una cuenta gratuita
3. Verifica tu email

---

## 📦 PASO 2: Crear bucket R2

1. En el dashboard de Cloudflare, ve a **R2**
2. Clic en **"Create bucket"**
3. Nombre del bucket: `productos-sync` (o el que prefieras)
4. Ubicación: **Automatic** (recomendado)
5. Clic en **"Create bucket"**

---

## 🔑 PASO 3: Obtener credenciales API

1. En R2, ve a **"Manage R2 API Tokens"**
2. Clic en **"Create API Token"**
3. Configuración:
   - **Token name:** `ProductosSync`
   - **Permissions:** `Object Read & Write`
   - **TTL:** `Forever` (o el tiempo que prefieras)
   - **Bucket:** Selecciona tu bucket `productos-sync`
4. Clic en **"Create API Token"**
5. **IMPORTANTE:** Copia y guarda:
   - `Access Key ID`
   - `Secret Access Key`
   - `Account ID` (aparece en la URL o en el dashboard)

---

## ⚙️ PASO 4: Configurar en ProductosSync

Edita el archivo `.env` en ProductosSync:

```env
# Habilitar Cloudflare R2
CLOUDFLARE_ENABLED=True

# Credenciales (las que copiaste en el paso anterior)
CLOUDFLARE_ACCOUNT_ID=tu_account_id_aqui
CLOUDFLARE_ACCESS_KEY_ID=tu_access_key_aqui
CLOUDFLARE_SECRET_ACCESS_KEY=tu_secret_key_aqui
CLOUDFLARE_BUCKET_NAME=productos-sync
```

---

## 🔄 PASO 5: Reinstalar dependencias

En el servidor, ejecuta:

```powershell
cd C:\Users\Servidor\Desktop\SyncProductosBD
.\venv\Scripts\pip.exe install -r requirements.txt
```

---

## 🚀 PASO 6: Reiniciar el servicio

```powershell
sc stop ProductosSyncAPI
timeout /t 2
sc start ProductosSyncAPI
```

---

## 🌐 PASO 7: Hacer el bucket público

Para que cualquiera pueda acceder a los archivos JSON:

1. En Cloudflare R2, abre tu bucket `productos-sync`
2. Ve a **"Settings"**
3. En **"Public access"**, clic en **"Allow Access"**
4. Copia la **"Public bucket URL"**
   - Ejemplo: `https://pub-abc123.r2.dev`

---

## ✅ PASO 8: Probar acceso

Después de 30 minutos (o reiniciar el servicio), accede a:

```
https://pub-abc123.r2.dev/inventario.json
https://pub-abc123.r2.dev/productos.json
https://pub-abc123.r2.dev/precios.json
```

Reemplaza `pub-abc123.r2.dev` con tu URL pública del bucket.

---

## 📊 Estructura de los archivos JSON

### inventario.json
```json
{
  "success": true,
  "total": 1272,
  "timestamp": "2026-04-17T15:30:00",
  "data": [
    {
      "codigo": "000001",
      "descripcion": "PRODUCTO EJEMPLO",
      "disponible": 50,
      "precio_venta_1": 15000,
      ...
    }
  ]
}
```

### productos.json
```json
{
  "success": true,
  "total": 9408,
  "timestamp": "2026-04-17T15:30:00",
  "data": [...]
}
```

### precios.json
```json
{
  "success": true,
  "total": 9408,
  "timestamp": "2026-04-17T15:30:00",
  "data": [...]
}
```

---

## 🔍 Verificar que funciona

### Ver logs del servicio:

```powershell
type C:\Users\Servidor\Desktop\SyncProductosBD\logs\app.log
```

Busca líneas como:
```
✓ Inventario subido a Cloudflare R2: 1272 productos
✓ Productos subidos a Cloudflare R2: 9408 productos
✓ Precios subidos a Cloudflare R2: 9408 precios
```

---

## 🎯 URLs finales para compartir

Una vez configurado, comparte estas URLs:

```
# Inventario completo
https://pub-abc123.r2.dev/inventario.json

# Solo productos
https://pub-abc123.r2.dev/productos.json

# Solo precios
https://pub-abc123.r2.dev/precios.json
```

---

## 💡 Ventajas de esta solución

| Característica | Con R2 | Sin R2 (Port Forwarding) |
|----------------|--------|--------------------------|
| Necesita Port Forwarding | ❌ No | ✅ Sí |
| Acceso al router | ❌ No | ✅ Sí |
| URL permanente | ✅ Sí | ✅ Sí |
| HTTPS | ✅ Sí | ❌ No (sin certificado) |
| Costo | ✅ Gratis | ✅ Gratis |
| Velocidad | ✅ CDN global | ⚠️ Depende de internet |
| Actualización | ⏱️ Cada 30 min | ⚡ Tiempo real |

---

## ⚠️ Limitaciones

- Los datos se actualizan cada 30 minutos (no en tiempo real)
- Solo lectura (no puedes hacer POST/PUT/DELETE)
- Límite de 10GB/mes en plan gratuito (más que suficiente para JSON)

---

## 🔧 Solución de problemas

### Error: "Error inicializando cliente R2"

Verifica que las credenciales en `.env` sean correctas.

### Error: "Error subiendo a Cloudflare R2"

1. Verifica que el bucket existe
2. Verifica que el token tenga permisos de escritura
3. Verifica que `CLOUDFLARE_ENABLED=True`

### No aparecen los archivos en R2

1. Espera 30 minutos (es el intervalo de sincronización)
2. O reinicia el servicio para forzar subida inmediata
3. Revisa los logs: `type logs\app.log`

### Error 403 al acceder a la URL pública

El bucket no está configurado como público. Ve al PASO 7.

---

## 📞 Resumen ejecutivo

```
1. Crear cuenta Cloudflare (gratis)
2. Crear bucket R2
3. Obtener credenciales API
4. Configurar .env con credenciales
5. Reinstalar dependencias (pip install)
6. Reiniciar servicio
7. Hacer bucket público
8. Acceder a: https://tu-bucket.r2.dev/inventario.json
```

**Tiempo total:** 10-15 minutos

---

## 🎉 ¡Listo!

Ahora tu inventario está accesible desde cualquier lugar del mundo sin necesidad de Port Forwarding.

Comparte la URL pública y cualquiera podrá consultar tu inventario en tiempo casi real (actualización cada 30 minutos).
