# 📋 INSTRUCCIONES PARA EL SERVIDOR

## 🔄 Actualizar el servicio con Cloudflare R2

Ya tienes el servicio instalado y funcionando. Ahora vamos a agregar Cloudflare R2 para exponer el inventario sin Port Forwarding.

---

## PASO 1: Actualizar dependencias

Abre PowerShell como ADMINISTRADOR en el servidor y ejecuta:

```powershell
cd C:\Users\Servidor\Desktop\SyncProductosBD

# Instalar nueva dependencia (boto3 para Cloudflare R2)
.\venv\Scripts\pip.exe install boto3==1.35.76
```

---

## PASO 2: Configurar Cloudflare (si quieres usarlo)

### Opción A: Usar Cloudflare R2 (sin Port Forwarding)

1. Sigue la guía: `GUIA_CLOUDFLARE_R2.md`
2. Obtén las credenciales de Cloudflare
3. Edita `.env` y configura:
   ```env
   CLOUDFLARE_ENABLED=True
   CLOUDFLARE_ACCOUNT_ID=tu_account_id
   CLOUDFLARE_ACCESS_KEY_ID=tu_access_key
   CLOUDFLARE_SECRET_ACCESS_KEY=tu_secret_key
   CLOUDFLARE_BUCKET_NAME=tu_bucket
   ```

### Opción B: NO usar Cloudflare (dejar como está)

Si prefieres usar Port Forwarding o no necesitas Cloudflare, simplemente deja:

```env
CLOUDFLARE_ENABLED=False
```

El servicio funcionará exactamente igual que antes.

---

## PASO 3: Reiniciar el servicio

```powershell
# Detener servicio
sc stop ProductosSyncAPI

# Esperar 2 segundos
timeout /t 2

# Iniciar servicio
sc start ProductosSyncAPI

# Verificar estado
sc query ProductosSyncAPI
```

---

## PASO 4: Verificar que funciona

### Si NO usas Cloudflare:
Todo sigue funcionando igual:
```
http://localhost:8090/health
http://192.168.18.121:8090/health
```

### Si SÍ usas Cloudflare:
Además de lo anterior, después de 30 minutos verás:
```
https://tu-bucket.r2.dev/inventario.json
```

---

## 🔍 Ver logs

```powershell
# Ver últimas líneas del log
Get-Content C:\Users\Servidor\Desktop\SyncProductosBD\logs\app.log -Tail 50

# Ver solo mensajes de Cloudflare
Get-Content C:\Users\Servidor\Desktop\SyncProductosBD\logs\app.log | Select-String "Cloudflare"
```

---

## ✅ Verificación rápida

```powershell
# 1. Verificar que el servicio está corriendo
sc query ProductosSyncAPI

# 2. Verificar que está escuchando en el puerto
netstat -ano | findstr "8090"

# 3. Probar localmente
Invoke-WebRequest -Uri "http://localhost:8090/health" -UseBasicParsing
```

---

## 🧪 Probar Cloudflare (opcional)

Si configuraste Cloudflare, prueba la conexión:

```powershell
cd C:\Users\Servidor\Desktop\SyncProductosBD
.\venv\Scripts\python.exe test_cloudflare.py
```

---

## 📊 Resumen de cambios

| Antes | Después |
|-------|---------|
| Solo API local | API local + Cloudflare R2 (opcional) |
| Requiere Port Forwarding | Cloudflare NO requiere Port Forwarding |
| Tiempo real | Tiempo real (local) + Cada 30 min (R2) |
| 1 forma de acceso | 2 formas de acceso |

---

## ⚠️ IMPORTANTE

- ✅ El servicio sigue funcionando EXACTAMENTE igual si no configuras Cloudflare
- ✅ Cloudflare es OPCIONAL
- ✅ Si Cloudflare falla, la API local sigue funcionando
- ✅ No hay riesgo de romper nada

---

## 🎯 URLs finales

### API Local (siempre disponible):
```
http://192.168.18.121:8090/api/inventario?api_key=aX7kR2mP9qL4nV6wZ1jT8cY3
```

### Cloudflare R2 (si lo configuras):
```
https://tu-bucket.r2.dev/inventario.json
```

---

## 📞 ¿Problemas?

1. Ver logs: `type logs\app.log`
2. Verificar servicio: `sc query ProductosSyncAPI`
3. Reiniciar: `sc stop ProductosSyncAPI && sc start ProductosSyncAPI`

---

## ✅ Checklist

- [ ] Instalar boto3: `.\venv\Scripts\pip.exe install boto3==1.35.76`
- [ ] Decidir si usar Cloudflare (opcional)
- [ ] Si usas Cloudflare: Configurar `.env`
- [ ] Reiniciar servicio: `sc stop/start ProductosSyncAPI`
- [ ] Verificar logs: `type logs\app.log`
- [ ] Probar acceso local: `http://localhost:8090/health`
- [ ] Si usas Cloudflare: Esperar 30 min y probar URL pública

---

**Tiempo estimado:** 5 minutos (sin Cloudflare) o 15 minutos (con Cloudflare)
