"""
Script de prueba para el endpoint de nicho climático
Prueba localmente el pipeline sin necesidad de un servidor corriendo
"""
import json
from climatic.climate_niche import ClimateNicheCalculator
from climatic.grid_sampling import GridSampler
from app.crud import crud_action


def test_calculate_climate_niche(id_species: int, sample_size: int = None):
    """
    Prueba el cálculo de nicho climático
    
    Uso:
        python test_climate_niche.py
    """
    print("\n" + "="*60)
    print(f"🌍 Probando cálculo de nicho climático")
    print(f"Especie ID: {id_species}")
    print("="*60)
    
    # Ejecutar cálculo
    result = ClimateNicheCalculator.calculate(
        id_species=id_species,
        sample_size=sample_size
    )
    
    print("\n" + "="*60)
    print("📊 RESULTADO:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


def test_get_occurrences(id_species: int):
    """
    Prueba obtener ocurrencias de una especie
    """
    print(f"\n📍 Obteniendo ocurrencias para especie {id_species}...")
    
    occurrences = crud_action(
        action="read",
        table="occurrences",
        where={"id_species": id_species}
    )
    
    print(f"✅ {len(occurrences)} ocurrencias encontradas\n")
    
    if occurrences:
        print("Primeras 3 ocurrencias:")
        for occ in occurrences[:3]:
            print(f"  - Lat: {occ.get('decimal_latitude')}, "
                  f"Lon: {occ.get('decimal_longitude')}, "
                  f"Elevación: {occ.get('elevation')}")
    
    return occurrences


def test_grid_sampling(id_species: int, sample_size: int = 20):
    """
    Prueba el muestreo inteligente por grid
    """
    print(f"\n🎯 Probando muestreo estratificado...")
    
    occurrences = crud_action(
        action="read",
        table="occurrences",
        where={"id_species": id_species}
    )
    
    if not occurrences:
        print("❌ No hay ocurrencias")
        return
    
    sampled = GridSampler.stratified_random_sample(
        occurrences,
        sample_size=sample_size,
        grid_resolution=5
    )
    
    print(f"✅ {len(occurrences)} → {len(sampled)} puntos después del muestreo")
    
    # Mostrar distribución por grid
    from collections import defaultdict
    grid_dist = defaultdict(int)
    
    for occ in sampled:
        cell = GridSampler.get_grid_cell(
            occ.get("decimal_latitude"),
            occ.get("decimal_longitude"),
            resolution=5
        )
        grid_dist[cell] += 1
    
    print(f"\n📊 Distribución por celda de grid ({len(grid_dist)} celdas):")
    for cell, count in sorted(grid_dist.items()):
        print(f"  {cell}: {count} puntos")
    
    return sampled


if __name__ == "__main__":
    # Prueba con especie 3 (Triticum aestivum - Trigo)
    id_species = 3
    
    print("\n" + "="*60)
    print("🌾 TEST: NICHO CLIMÁTICO DE TRITICUM AESTIVUM")
    print("="*60)
    
    # Paso 1: Verificar ocurrencias
    test_get_occurrences(id_species)
    
    # Paso 2: Probar muestreo
    test_grid_sampling(id_species, sample_size=30)
    
    # Paso 3: Calcular nicho climático
    result = test_calculate_climate_niche(id_species, sample_size=30)
    
    # Paso 4: Guardar resultado
    if "error" not in result:
        print("\n" + "="*60)
        print("💾 Guardando resultado en BD...")
        print("="*60)
        
        save_result = crud_action(
            action="create",
            table="climate_requirements",
            data={
                "id_species": result["id_species"],
                "temp_min": result.get("temp_min"),
                "temp_opt_min": result.get("temp_opt_min"),
                "temp_opt_max": result.get("temp_opt_max"),
                "temp_max": result.get("temp_max"),
                "rainfall_min": result.get("rainfall_min"),
                "rainfall_opt_min": result.get("rainfall_opt_min"),
                "rainfall_opt_max": result.get("rainfall_opt_max"),
                "rainfall_max": result.get("rainfall_max"),
                "altitude_min": result.get("altitude_min"),
                "altitude_max": result.get("altitude_max"),
            }
        )
        print(f"✅ Resultado guardado\n{json.dumps(save_result, indent=2)}")
    else:
        print(f"\n❌ Error en cálculo: {result['error']}")
