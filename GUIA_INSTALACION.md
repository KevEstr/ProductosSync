# 📘 GUÍA DE INSTALACIÓN PASO A PASO

Esta guía te llevará desde cero hasta tener tu API funcionando y accesible desde cualquier PC del mundo.

## 📋 REQUISITOS PREVIOS

1. ✅ Windows (cualquier versión moderna)
2. ✅ Python 3.8 o superior instalado
3. ✅ Acceso a la carpeta DbfRed con los archivos de la base de datos
4. ✅ Permisos de administrador en el PC

## 🚀 PASO 1: VERIFICAR PYTHON

Abre PowerShell o CMD y ejecuta:

```bash
python --version
```

Deberías ver algo como: `Python 3.11.0`

Si no tienes Python:
1. Descarga desde: https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia el PC después de instalar

## 📁 PASO 2: VERIFICAR ESTRUCTURA DE CARPETAS

Tu estructura debe verse así:

```
📁 Carpeta Principal/
├── 📁 ProductosSync/          ← Proyecto de la API
│   ├── 📁 src/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   ├── run.bat
│   └── instalar_servicio.bat
└── 📁 DbfRed/                 ← Base de datos DBF
    ├── Producto.DBF
    ├── MovMes.DBF
    └── ... (otros archivos)
```

## ⚙️ PASO 3: CONFIGURAR LA API

1. Abre el archivo `.env` en ProductosSync con Notepad

2. Verifica/modifica estas líneas:

```env
# Ruta a los archivos DBF (relativa desde ProductosSync)
DBF_PATH=../DbfRed

# Clave de seguridad (CÁMBIALA por una única)
API_KEY=mi_clave_secreta_123456

# Puerto (5000 es el estándar)
PORT=5000
```

3. Guarda el archivo

## 🔧 PASO 4: INSTALAR COMO SERVICIO DE WINDOWS

1. Ve a la carpeta ProductosSync

2. Haz clic derecho en `instalar_servicio.bat`

3. Selecciona "Ejecutar como administrador"

4. El instalador hará automáticamente:
   - ✅ Buscar Python
   - ✅ Crear entorno virtual
   - ✅ Instalar dependencias
   - ✅ Descargar NSSM (gestor de servicios)
   - ✅ Configurar el servicio
   - ✅ Abrir puerto en firewall

5. Cuando te pida credenciales:
   ```
   Usuario: Administrador
   Contraseña: [tu contraseña de Windows]
   ```
   (O el usuario con el que inicias sesión)

6. Al finalizar verás:
   ```
   ============================================================
     INSTALACION COMPLETADA
   ============================================================
   ```

## ✅ PASO 5: VERIFICAR QUE FUNCIONA

### Prueba Local

1. Abre tu navegador

2. Ve a: http://localhost:5000/health

3. Deberías ver:
```json
{
  "status": "healthy",
  "timestamp": "2025-02-14T10:30:00",
  "dbf_path": "..\\DbfRed",
  "cache_activo": true
}
```

### Prueba desde otro PC en la misma red

1. Obtén tu IP local:
   - Abre CMD
   - Ejecuta: `ipconfig`
   - Busca "IPv4": ejemplo `192.168.1.100`

2. Desde otro PC en la misma red, abre navegador:
   ```
   http://192.168.1.100:5000/health
   ```

3. Si funciona, ¡tu API está corriendo! 🎉

## 🌐 PASO 6: EXPONER AL INTERNET (ACCESO MUNDIAL)

Ahora viene la parte importante: hacer que cualquier PC del mundo pueda acceder.

### Método 1: Port Forwarding en Router (RECOMENDADO)

#### 6.1. Obtener tu IP local

```bash
ipconfig
```
Anota tu IPv4 (ejemplo: 192.168.1.100)

#### 6.2. Acceder al router

1. Abre navegador
2. Ve a: http://192.168.1.1 (o http://192.168.0.1)
3. Usuario/contraseña:
   - Común: admin/admin
   - O revisa la etiqueta del router
   - O llama a tu proveedor de internet

#### 6.3. Configurar Port Forwarding

Busca la sección (varía según router):
- "Port Forwarding"
- "Virtual Server"
- "NAT"
- "Aplicaciones y Juegos"

Crea una nueva regla:
```
Nombre: ProductosSync API
Puerto Externo: 5000
Puerto Interno: 5000
IP Interna: 192.168.1.100 (tu IP local)
Protocolo: TCP
Estado: Habilitado
```

Guarda y aplica cambios.

#### 6.4. Obtener tu IP pública

1. Ve a: https://www.whatismyip.com/
2. Anota tu IP pública (ejemplo: 203.0.113.45)

#### 6.5. Probar acceso externo

Desde un celular (usando datos móviles, NO WiFi):

```
http://203.0.113.45:5000/health
```

Si funciona, ¡ya está accesible desde internet! 🌍

### Método 2: ngrok (Más fácil, para pruebas)

Si no puedes configurar el router, usa ngrok:

1. Descarga ngrok: https://ngrok.com/download

2. Descomprime y ejecuta:
```bash
ngrok http 5000
```

3. Verás algo como:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

4. Usa esa URL desde cualquier lugar:
```
https://abc123.ngrok.io/api/inventario?api_key=tu_clave
```

⚠️ NOTA: La URL de ngrok cambia cada vez que lo reinicias (versión gratuita)

## 🔐 PASO 7: USAR LA API

### Ejemplo con navegador

```
http://TU_IP_PUBLICA:5000/api/inventario?api_key=mi_clave_secreta_123456&limit=10
```

### Ejemplo con curl

```bash
curl -H "X-API-Key: mi_clave_secreta_123456" http://TU_IP_PUBLICA:5000/api/inventario
```

### Ejemplo con Python

```python
import requests

url = "http://TU_IP_PUBLICA:5000/api/inventario"
headers = {"X-API-Key": "mi_clave_secreta_123456"}

response = requests.get(url, headers=headers)
print(response.json())
```

### Ejemplo con JavaScript

```javascript
fetch('http://TU_IP_PUBLICA:5000/api/inventario', {
  headers: {
    'X-API-Key': 'mi_clave_secreta_123456'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📊 PASO 8: MONITOREAR EL SERVICIO

### Ver si está corriendo

```bash
sc query ProductosSyncAPI
```

### Ver logs en tiempo real

```bash
type logs\app.log
```

O abre el archivo con Notepad: `ProductosSync\logs\app.log`

### Reiniciar el servicio

```bash
sc stop ProductosSyncAPI
timeout /t 2
sc start ProductosSyncAPI
```

## 🛠️ SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Python no encontrado"

Instala Python desde https://www.python.org/downloads/
Marca "Add Python to PATH" durante instalación

### ❌ Error: "Ruta DBF no encontrada"

1. Verifica que la carpeta DbfRed existe
2. Verifica la ruta en `.env`:
   ```env
   DBF_PATH=../DbfRed
   ```
3. Si DbfRed está en otro lugar, ajusta la ruta

### ❌ Error: "API key requerida"

Incluye la API key en tus peticiones:
- Header: `X-API-Key: tu_clave`
- O parámetro: `?api_key=tu_clave`

### ❌ No puedo acceder desde otro PC

1. Verifica que el servicio está corriendo:
   ```bash
   sc query ProductosSyncAPI
   ```

2. Verifica el firewall:
   - Windows Defender Firewall
   - Busca regla "ProductosSyncAPI"
   - Debe estar habilitada

3. Prueba primero en local: http://localhost:5000/health

4. Luego en red local: http://192.168.1.100:5000/health

5. Finalmente desde internet: http://TU_IP_PUBLICA:5000/health

### ❌ El servicio se detiene solo

1. Revisa logs:
   ```bash
   type logs\service_err.log
   ```

2. Verifica que las credenciales de Windows sean correctas

3. Reinstala el servicio:
   - Ejecuta `desinstalar_servicio.bat` (como admin)
   - Ejecuta `instalar_servicio.bat` (como admin)

## 🎯 RESUMEN DE URLs

Una vez instalado, estos son tus endpoints:

```
# Local
http://localhost:5000/health
http://localhost:5000/api/inventario?api_key=TU_CLAVE

# Red local
http://192.168.1.100:5000/health
http://192.168.1.100:5000/api/inventario?api_key=TU_CLAVE

# Internet (después de Port Forwarding)
http://TU_IP_PUBLICA:5000/health
http://TU_IP_PUBLICA:5000/api/inventario?api_key=TU_CLAVE
```

## ✅ CHECKLIST FINAL

- [ ] Python instalado y funcionando
- [ ] Carpeta DbfRed accesible
- [ ] Archivo .env configurado
- [ ] Servicio instalado correctamente
- [ ] Funciona en local (localhost:5000)
- [ ] Funciona en red local (192.168.x.x:5000)
- [ ] Port Forwarding configurado en router
- [ ] Funciona desde internet (IP_PUBLICA:5000)
- [ ] API Key configurada y funcionando

## 🎉 ¡LISTO!

Tu API está funcionando y accesible desde cualquier parte del mundo.

Comparte tu URL con quien necesite acceder:
```
http://TU_IP_PUBLICA:5000/api/inventario?api_key=TU_CLAVE
```

Para soporte, revisa los logs en: `ProductosSync\logs\app.log`
