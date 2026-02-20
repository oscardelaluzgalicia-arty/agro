"""
Script de prueba para el Traductor Semántico
Prueba los componentes del sistema sin necesidad de hacer requests HTTP
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()


def test_translator():
    """Prueba el módulo traductor de IA"""
    print("\n" + "="*60)
    print("PRUEBA 1: Traductor IA")
    print("="*60)
    
    try:
        from traductorsemantico_ia.translator import get_translator
        
        translator = get_translator()
        print("OK - Translator inicializado correctamente")
        
        # Prueba con un nombre común
        test_names = ["uva", "manzana", "tomate"]
        
        for common_name in test_names:
            print(f"\nTradduciendo: '{common_name}'")
            scientific_names = translator.translate_to_scientific_names(common_name)
            
            print(f"  Nombres científicos encontrados: {len(scientific_names)}")
            for i, name in enumerate(scientific_names, 1):
                print(f"    {i}. {name}")
        
        print("\nOK - Prueba de Translator exitosa!")
        return True
        
    except Exception as e:
        print(f"\nERROR - Error en Translator: {str(e)}")
        return False


def test_gbif_validator():
    """Prueba el módulo validador GBIF"""
    print("\n" + "="*60)
    print("PRUEBA 2: Validador GBIF")
    print("="*60)
    
    try:
        from traductorsemantico_ia.gbif_validator import get_validator
        
        validator = get_validator()
        print("OK - Validator inicializado correctamente")
        
        # Prueba con nombres científicos conocidos
        test_names = [
            "Vitis vinifera",
            "Solanum lycopersicum",
            "Malus domestica",
            "Nombre inexistente xyz"
        ]
        
        print("\nValidando nombres científicos:")
        for name in test_names:
            result = validator.validate(name)
            if result:
                print(f"  OK - {name}")
                print(f"     - Confianza: {result['confidence']}%")
                print(f"     - Rango: {result['rank']}")
                print(f"     - Estado: {result['status']}")
            else:
                print(f"  ERROR - {name} (no validado)")
        
        print("\nOK - Prueba de Validator exitosa!")
        return True
        
    except Exception as e:
        print(f"\nERROR - Error en Validator: {str(e)}")
        return False


def test_full_pipeline():
    """Prueba el pipeline completo: IA + GBIF"""
    print("\n" + "="*60)
    print("PRUEBA 3: Pipeline Completo (IA + GBIF)")
    print("="*60)
    
    try:
        from traductorsemantico_ia.translator import get_translator
        from traductorsemantico_ia.gbif_validator import get_validator
        
        translator = get_translator()
        validator = get_validator()
        
        common_names = ["uva", "manzana"]
        
        for common_name in common_names:
            print(f"\nProcesando: '{common_name}'")
            print("   Paso 1: Traduciendo con IA...")
            
            scientific_names = translator.translate_to_scientific_names(common_name)
            print(f"   {len(scientific_names)} nombres científicos generados")
            
            print("   Paso 2: Validando con GBIF...")
            validated = validator.validate_multiple(scientific_names)
            print(f"   {len(validated)} nombres validados exitosamente")
            
            for result in validated:
                gbif = result["gbifData"]
                print(f"\n   OK - {result['inputName']}")
                print(f"      - Nombre científico: {gbif['scientificName']}")
                print(f"      - Confianza: {gbif['confidence']}%")
                print(f"      - TaxonKey: {gbif['usageKey']}")
                print(f"      - Rango: {gbif['rank']}")
        
        print("\nOK - Pipeline completo exitoso!")
        return True
        
    except Exception as e:
        print(f"\nERROR - Error en pipeline: {str(e)}")
        return False


def test_config():
    """Verifica la configuración"""
    print("\n" + "="*60)
    print("PRUEBA 0: Verificacion de Configuracion")
    print("="*60)
    
    # Verificar .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"OK - Archivo .env encontrado: {env_file}")
    else:
        print(f"ERROR - Archivo .env NO encontrado")
        return False
    
    # Verificar OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        print(f"OK - OPENAI_API_KEY esta configurada")
    else:
        print(f"ERROR - OPENAI_API_KEY no esta configurada correctamente")
        print(f"   Por favor, edita .env y reemplaza 'your-api-key-here' con tu clave real")
        return False
    
    # Verificar módulos
    required_modules = [
        "traductorsemantico_ia.config",
        "traductorsemantico_ia.translator",
        "traductorsemantico_ia.gbif_validator",
    ]
    
    print("\nVerificando modulos:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"  OK - {module}")
        except ImportError as e:
            print(f"  ERROR - {module}: {str(e)}")
            return False
    
    return True


def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PRUEBAS DEL TRADUCTOR SEMANTICO" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Configuración": test_config(),
    }
    
    # Solo ejecutar pruebas si la configuración es correcta
    if results["Configuración"]:
        results["Translator"] = test_translator()
        results["Validator"] = test_gbif_validator()
        results["Pipeline Completo"] = test_full_pipeline()
    else:
        print("\nADVERTENCIA - Configuracion incompleta. Saltando otras pruebas.")
    
    # Reporte final
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "OK - PASO" if passed else "ERROR - FALLO"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n{'Total':.<40} {total_passed}/{total_tests} pruebas exitosas")
    
    if total_passed == total_tests:
        print("\nOK - Todo funciona correctamente!")
    else:
        print("\nADVERTENCIA - Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("\n")


if __name__ == "__main__":
    main()
