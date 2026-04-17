"""
Script de prueba para verificar que la API funciona correctamente
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8090"
API_KEY = "mi_clave_secreta_123456"  # Cambia esto si usaste otra clave

# Headers con API Key
headers = {
    "X-API-Key": API_KEY
}

def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_health():
    """Prueba el endpoint de health check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Health check EXITOSO")
            return True
        else:
            print("❌ Health check FALLÓ")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Prueba el endpoint raíz"""
    print_section("TEST 2: Endpoint Raíz")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Endpoint raíz EXITOSO")
            return True
        else:
            print("❌ Endpoint raíz FALLÓ")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_inventario():
    """Prueba el endpoint de inventario"""
    print_section("TEST 3: Inventario (primeros 5 productos)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/inventario",
            headers=headers,
            params={"limit": 5},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de productos: {data.get('total', 0)}")
            print(f"Timestamp: {data.get('timestamp', 'N/A')}")
            
            if data.get('data'):
                print("\nPrimeros productos:")
                for i, producto in enumerate(data['data'][:3], 1):
                    print(f"\n  Producto {i}:")
                    print(f"    Código: {producto.get('codigo', 'N/A')}")
                    print(f"    Descripción: {producto.get('descripcion', 'N/A')}")
                    print(f"    Disponible: {producto.get('disponible', 0)}")
                    print(f"    Precio: ${producto.get('precio_venta_1', 0):,.2f}")
            
            print("\n✅ Inventario EXITOSO")
            return True
        else:
            print(f"❌ Inventario FALLÓ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_productos():
    """Prueba el endpoint de productos"""
    print_section("TEST 4: Productos (primeros 3)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/productos",
            headers=headers,
            params={"limit": 3},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de productos: {data.get('total', 0)}")
            print("✅ Productos EXITOSO")
            return True
        else:
            print(f"❌ Productos FALLÓ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_precios():
    """Prueba el endpoint de precios"""
    print_section("TEST 5: Precios (primeros 3)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/precios",
            headers=headers,
            params={"limit": 3},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de precios: {data.get('total', 0)}")
            print("✅ Precios EXITOSO")
            return True
        else:
            print(f"❌ Precios FALLÓ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sin_api_key():
    """Prueba que la API rechaza peticiones sin API Key"""
    print_section("TEST 6: Seguridad (sin API Key)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/inventario", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Seguridad funcionando correctamente (rechazó petición sin API Key)")
            return True
        else:
            print("❌ PROBLEMA DE SEGURIDAD: Aceptó petición sin API Key")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 80)
    print("  PRUEBAS DE LA API - ProductosSync")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    # Ejecutar tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Endpoint Raíz", test_root()))
    results.append(("Inventario", test_inventario()))
    results.append(("Productos", test_productos()))
    results.append(("Precios", test_precios()))
    results.append(("Seguridad", test_sin_api_key()))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! La API está funcionando correctamente.")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los logs para más detalles.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
