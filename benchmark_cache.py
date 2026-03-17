"""
Benchmark del sistema de caché - Product-Sync API
Mide tiempos de respuesta y rendimiento
"""
import requests
import time
import statistics
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = "http://localhost:5000"

def medir_tiempo(func, descripcion, repeticiones=10):
    """Mide el tiempo de ejecución de una función"""
    print(f"\n{'='*60}")
    print(f"📊 {descripcion}")
    print('='*60)
    
    tiempos = []
    errores = 0
    
    for i in range(repeticiones):
        try:
            inicio = time.time()
            resultado = func()
            fin = time.time()
            tiempo_ms = (fin - inicio) * 1000
            tiempos.append(tiempo_ms)
            
            if i == 0:
                print(f"Primera petición: {tiempo_ms:.2f} ms")
                if hasattr(resultado, 'json'):
                    data = resultado.json()
                    if 'total' in data:
                        print(f"Registros obtenidos: {data['total']}")
        except Exception as e:
            errores += 1
            print(f"❌ Error en petición {i+1}: {e}")
    
    if tiempos:
        print(f"\n📈 Estadísticas ({len(tiempos)} peticiones exitosas):")
        print(f"   Promedio: {statistics.mean(tiempos):.2f} ms")
        print(f"   Mínimo: {min(tiempos):.2f} ms")
        print(f"   Máximo: {max(tiempos):.2f} ms")
        print(f"   Mediana: {statistics.median(tiempos):.2f} ms")
        if len(tiempos) > 1:
            print(f"   Desv. Est.: {statistics.stdev(tiempos):.2f} ms")
    
    if errores > 0:
        print(f"\n⚠️  Errores: {errores}/{repeticiones}")
    
    return tiempos

def test_inventario_completo():
    """Prueba endpoint de inventario completo"""
    headers = {'X-API-Key': API_KEY}
    return requests.get(f"{BASE_URL}/api/inventario", headers=headers, timeout=30)

def test_inventario_limitado():
    """Prueba endpoint con límite"""
    headers = {'X-API-Key': API_KEY}
    return requests.get(f"{BASE_URL}/api/inventario?limit=100", headers=headers, timeout=30)

def test_inventario_disponible():
    """Prueba endpoint solo disponibles"""
    headers = {'X-API-Key': API_KEY}
    return requests.get(f"{BASE_URL}/api/inventario?disponible_solo=true", 
                       headers=headers, timeout=30)

def test_productos():
    """Prueba endpoint de productos"""
    headers = {'X-API-Key': API_KEY}
    return requests.get(f"{BASE_URL}/api/productos", headers=headers, timeout=30)

def test_precios():
    """Prueba endpoint de precios"""
    headers = {'X-API-Key': API_KEY}
    return requests.get(f"{BASE_URL}/api/precios", headers=headers, timeout=30)

def test_health():
    """Prueba health check"""
    return requests.get(f"{BASE_URL}/health", timeout=10)

def test_carga_concurrente():
    """Simula carga concurrente"""
    import concurrent.futures
    
    print(f"\n{'='*60}")
    print("🔥 Prueba de Carga Concurrente")
    print('='*60)
    
    def peticion_rapida():
        headers = {'X-API-Key': API_KEY}
        inicio = time.time()
        requests.get(f"{BASE_URL}/api/inventario?limit=10", headers=headers, timeout=10)
        return (time.time() - inicio) * 1000
    
    num_peticiones = 50
    num_workers = 10
    
    print(f"Enviando {num_peticiones} peticiones con {num_workers} workers...")
    inicio_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        tiempos = list(executor.map(lambda _: peticion_rapida(), range(num_peticiones)))
    
    fin_total = time.time()
    tiempo_total = fin_total - inicio_total
    
    print(f"\n📊 Resultados:")
    print(f"   Tiempo total: {tiempo_total:.2f} segundos")
    print(f"   Peticiones/segundo: {num_peticiones/tiempo_total:.2f}")
    print(f"   Tiempo promedio por petición: {statistics.mean(tiempos):.2f} ms")
    print(f"   Tiempo mínimo: {min(tiempos):.2f} ms")
    print(f"   Tiempo máximo: {max(tiempos):.2f} ms")

def main():
    print("="*60)
    print("🚀 BENCHMARK - Product-Sync API Cache System")
    print("="*60)
    print(f"URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ Error: El servidor no responde correctamente")
            print("   Asegúrate de que el servidor esté corriendo: python app.py")
            return
    except Exception as e:
        print(f"\n❌ Error: No se puede conectar al servidor")
        print(f"   {e}")
        print("\n   Asegúrate de que el servidor esté corriendo: python app.py")
        return
    
    print("✅ Servidor conectado\n")
    
    # Pruebas secuenciales
    tests = [
        (test_health, "Health Check (sin caché)", 5),
        (test_inventario_completo, "Inventario Completo (caché principal)", 20),
        (test_inventario_limitado, "Inventario Limitado (100 items)", 20),
        (test_inventario_disponible, "Solo Disponibles (filtrado)", 20),
        (test_productos, "Productos (caché secundario)", 10),
        (test_precios, "Precios (caché secundario)", 10),
    ]
    
    resultados = {}
    for func, desc, reps in tests:
        tiempos = medir_tiempo(func, desc, reps)
        if tiempos:
            resultados[desc] = statistics.mean(tiempos)
    
    # Prueba de carga
    try:
        test_carga_concurrente()
    except Exception as e:
        print(f"\n⚠️  Error en prueba de carga: {e}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📋 RESUMEN DE RENDIMIENTO")
    print('='*60)
    
    if resultados:
        for desc, tiempo_promedio in resultados.items():
            emoji = "🟢" if tiempo_promedio < 50 else "🟡" if tiempo_promedio < 200 else "🔴"
            print(f"{emoji} {desc}: {tiempo_promedio:.2f} ms")
    
    print(f"\n{'='*60}")
    print("💡 INTERPRETACIÓN")
    print('='*60)
    print("🟢 < 50 ms   = EXCELENTE (caché funcionando perfectamente)")
    print("🟡 50-200 ms = BUENO (caché activo, red/procesamiento normal)")
    print("🔴 > 200 ms  = LENTO (posible problema o sin caché)")
    
    print(f"\n{'='*60}")
    print("✅ Benchmark completado")
    print('='*60)

if __name__ == '__main__':
    main()
