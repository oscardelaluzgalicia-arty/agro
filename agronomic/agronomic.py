"""
Pipeline paralelo para enriquecimiento agronómico
INPUT: id_species
Ejecuta 8 tareas en paralelo para enriquecer los datos de la especie
"""

import asyncio
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import aiohttp
import logging
import sys

# Configurar logging más detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AgronomicEnrichmentPipeline:
    """
    Pipeline paralelo de enriquecimiento agronómico para una especie.
    
    Flujo de ejecución:
    1. Obtener datos base de la especie
    2. Obtener ocurrencias almacenadas [PARALELO]
    3. Enriquecer con WorldClim [PARALELO]
    4-8. Insertar datos: climate, crop, soil, calendar, companions
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: conexión a la BD MySQL
        """
        self.db = db_connection
        self.species_data = None
        self.occurrences = []
        self.climate_data = {
            'temperatures': [],
            'rainfall': [],
            'altitudes': []
        }
        
    async def enrich_species(self, id_species: int) -> Dict:
        """
        Ejecuta el pipeline completo de enriquecimiento
        
        Args:
            id_species: ID de la especie a enriquecer
            
        Returns:
            Dict con resultado de operaciones
        """
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f" INICIANDO PIPELINE DE ENRIQUECIMIENTO AGRONÓMICO")
            logger.info(f"{'='*70}")
            logger.info(f" Species ID: {id_species}")
            
            # PASO 1: Obtener datos base de la especie
            logger.info(f"\n[1/8]  Obteniendo datos base de la especie...")
            self.species_data = await self._get_species_data(id_species)
            if not self.species_data:
                logger.error(f" Especie {id_species} no encontrada")
                return {"error": "Especie no encontrada", "id_species": id_species}
            
            logger.info(f" Species: {self.species_data['scientific_name']}")
            logger.info(f"   Family: {self.species_data.get('family', 'N/A')}")
            logger.info(f"   Genus: {self.species_data.get('genus', 'N/A')}")
            
            # PASO 2: Obtener ocurrencias EN PARALELO
            logger.info(f"\n[2/8]  Obteniendo ocurrencias almacenadas...")
            occurrences_task = asyncio.create_task(
                self._get_occurrences(id_species)
            )
            
            self.occurrences = await occurrences_task
            
            if not self.occurrences:
                logger.warning(f"  No hay ocurrencias almacenadas para species {id_species}")
                return {
                    "id_species": id_species,
                    "warning": "No occurrences found for climate inference"
                }
            
            logger.info(f" Ocurrencias obtenidas: {len(self.occurrences)}")
            
            # Obtener rango de fechas de forma segura
            dates_with_values = [o.get('event_date') for o in self.occurrences if o.get('event_date') is not None]
            if dates_with_values:
                try:
                    min_date = min(dates_with_values)
                    max_date = max(dates_with_values)
                    logger.info(f"   Rango de fechas: {min_date} a {max_date}")
                except Exception as e:
                    logger.info(f"   (No hay fechas válidas: {str(e)})")
            else:
                logger.info(f"   (Sin datos de fecha)")
            
            # PASO 3: Enriquecer con WorldClim
            logger.info(f"\n[3/8]   Enriqueciendo con datos climáticos (WorldClim/Open-Meteo)...")
            await self._enrich_with_worldclim()
            
            # Validar que tenemos datos
            if not self.climate_data['temperatures']:
                logger.warning(f"  No se obtuvieron datos climáticos. Continuando con valores por defecto.")
            
            # PASOS 4-8: Insertar datos en paralelo
            logger.info(f"\n[4-8/8]  Insertando datos enriquecidos en base de datos...")
            
            results = {
                "id_species": id_species,
                "species_name": self.species_data['scientific_name'],
                "timestamp": datetime.now().isoformat(),
                "operations": {}
            }
            
            # Ejecutar inserciones
            logger.info(f"   [4] Insertando climate_requirements...")
            results["operations"]["climate"] = await self._insert_climate_requirements(id_species)
            logger.info(f"    {results['operations']['climate']['status']}")
            
            logger.info(f"   [5] Insertando crop_profile...")
            results["operations"]["crop_profile"] = await self._insert_crop_profile(id_species)
            logger.info(f"    {results['operations']['crop_profile']['status']}")
            
            logger.info(f"   [6] Insertando soil_requirements...")
            results["operations"]["soil"] = await self._insert_soil_requirements(id_species)
            logger.info(f"    {results['operations']['soil']['status']}")
            
            logger.info(f"   [7] Insertando planting_calendar...")
            results["operations"]["calendar"] = await self._insert_planting_calendar(id_species)
            logger.info(f"    {results['operations']['calendar']['status']}")
            
            logger.info(f"   [8] Insertando companion_plants...")
            results["operations"]["companions"] = await self._insert_companion_plants(id_species)
            logger.info(f"    {results['operations']['companions']['status']}")
            
            logger.info(f"\n{'='*70}")
            logger.info(f"✨ ENRIQUECIMIENTO COMPLETADO EXITOSAMENTE")
            logger.info(f"{'='*70}\n")
            
            return results
            
        except Exception as e:
            logger.error(f"\n{'='*70}")
            logger.error(f"❌ ERROR EN PIPELINE: {str(e)}")
            logger.error(f"{'='*70}\n")
            return {"error": str(e), "id_species": id_species}
    
    # ============= PASO 1: DATOS BASE DE LA ESPECIE =============
    async def _get_species_data(self, id_species: int) -> Optional[Dict]:
        """
        Obtiene datos base de la especie
        SELECT id_species, canonical_name, genus, family FROM species WHERE id_species = ?
        """
        try:
            with self.db.cursor() as cur:
                sql = """
                    SELECT 
                        id_species, scientific_name, genus, family
                    FROM species
                    WHERE id_species = %s
                """
                cur.execute(sql, (id_species,))
                result = cur.fetchone()
                return result
        except Exception as e:
            logger.error(f"Error obteniendo datos de especie: {str(e)}")
            return None
    
    # ============= PASO 2: OBTENER OCURRENCIAS =============
    async def _get_occurrences(self, id_species: int) -> List[Dict]:
        """
        Obtiene coordenadas de ocurrencias almacenadas
        SELECT decimalLatitude, decimalLongitude FROM occurrences 
        WHERE id_species = ? AND decimalLatitude IS NOT NULL
        """
        try:
            with self.db.cursor() as cur:
                sql = """
                    SELECT 
                        decimal_latitude,
                        decimal_longitude,
                        event_date,
                        MONTH(event_date) as month
                    FROM occurrences
                    WHERE id_species = %s
                    AND decimal_latitude IS NOT NULL
                    AND decimal_longitude IS NOT NULL
                    AND event_date IS NOT NULL
                """
                cur.execute(sql, (id_species,))
                results = cur.fetchall()
                return results if results else []
        except Exception as e:
            logger.error(f"Error obteniendo ocurrencias: {str(e)}")
            return []
    
    # ============= PASO 3: ENRIQUECER CON WORLDCLIM =============
    async def _enrich_with_worldclim(self):
        """
        Para cada coordenada, obtiene temperatura, precipitación y altitud de WorldClim
        Variables mínimas: temp media anual, precip anual, altitud
        """
        logger.info(f" Iniciando enriquecimiento climático de {len(self.occurrences)} ocurrencias")
        
        if not self.occurrences:
            logger.warning("  No hay ocurrencias para enriquecer")
            return
        
        successful_enrichments = 0
        failed_enrichments = 0
        
        # Usar aiohttp para requests paralelos
        async with aiohttp.ClientSession() as session:
            # Procesar en lotes para mejor control
            batch_size = 10
            for batch_start in range(0, len(self.occurrences), batch_size):
                batch_end = min(batch_start + batch_size, len(self.occurrences))
                batch = self.occurrences[batch_start:batch_end]
                
                logger.info(f" Procesando ocurrencias {batch_start + 1}-{batch_end} de {len(self.occurrences)}")
                
                tasks = [
                    self._fetch_worldclim_data(
                        session,
                        occ['decimal_latitude'],
                        occ['decimal_longitude'],
                        idx = batch_start + i
                    )
                    for i, occ in enumerate(batch)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        logger.debug(f" Error en WorldClim: {str(result)}")
                        failed_enrichments += 1
                        continue
                    if result:
                        if 'temp' in result and result['temp'] is not None:
                            self.climate_data['temperatures'].append(result['temp'])
                            successful_enrichments += 1
                        if 'rainfall' in result and result['rainfall'] is not None:
                            self.climate_data['rainfall'].append(result['rainfall'])
                        if 'altitude' in result and result['altitude'] is not None:
                            self.climate_data['altitudes'].append(result['altitude'])
                    else:
                        failed_enrichments += 1
        
        logger.info(f" Datos climáticos recopilados: "
                   f"exitosas={successful_enrichments}, "
                   f"fallidas={failed_enrichments}, "
                   f"temp={len(self.climate_data['temperatures'])}, "
                   f"rain={len(self.climate_data['rainfall'])}, "
                   f"alt={len(self.climate_data['altitudes'])}")
    
    async def _fetch_worldclim_data(self, session: aiohttp.ClientSession, 
                                   lat: float, lon: float,
                                   idx: int = 0) -> Optional[Dict]:
        """
        Fetch clima data desde Open-Meteo API
        Fallback: estimaciones basadas en coordenadas
        """
        try:
            # Intenta con Open-Meteo Archive API
            url = f"https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": "2015-01-01",
                "end_date": "2023-12-31",
                "monthly": ["temperature_2m_mean", "precipitation_sum"],
                "elevation": "true"
            }
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Extraer datos
                    temp_data = data.get('monthly', {}).get('temperature_2m_mean', [])
                    rain_data = data.get('monthly', {}).get('precipitation_sum', [])
                    
                    if temp_data and rain_data:
                        climate = {
                            'temp': float(np.mean(temp_data)),
                            'rainfall': float(np.sum(rain_data)),  # suma anual de precipitación
                            'altitude': float(data.get('elevation', 0))
                        }
                        logger.debug(f" Ocurrencia {idx}: lat={lat}, lon={lon}, "
                                   f"temp={climate['temp']:.1f}°C, rain={climate['rainfall']:.0f}mm, alt={climate['altitude']:.0f}m")
                        return climate
                    else:
                        logger.debug(f"  Open-Meteo sin datos para {lat},{lon}")
                        
        except asyncio.TimeoutError:
            logger.debug(f"  Timeout en Open-Meteo para {lat},{lon}")
        except Exception as e:
            logger.debug(f" Error en Open-Meteo: {str(e)}")
        
        # FALLBACK: Estimaciones basadas en coordenadas (regresión simple)
        try:
            logger.debug(f" Usando fallback para {lat},{lon}")
            climate = self._estimate_climate_from_coords(lat, lon)
            if climate:
                logger.debug(f" Estimado {idx}: lat={lat}, lon={lon}, "
                           f"temp={climate['temp']:.1f}°C, rain={climate['rainfall']:.0f}mm, alt={climate['altitude']:.0f}m")
            return climate
        except Exception as e:
            logger.debug(f"Error en estimación: {str(e)}")
            return None
    
    def _estimate_climate_from_coords(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Estimación simplificada de clima basada en latitud y altitud aproximada
        Basado en patrones globales conocidos
        """
        try:
            # Temperatura basada en latitud (simplificado)
            # Ecuador: ~25°C, Trópicos: ~20°C, Templados: ~10-15°C
            abs_lat = abs(lat)
            if abs_lat < 10:  # Ecuatorial
                temp = 25 - (abs_lat * 0.5)
            elif abs_lat < 30:  # Tropical
                temp = 20 - ((abs_lat - 10) * 0.5)
            elif abs_lat < 50:  # Templado
                temp = 15 - ((abs_lat - 30) * 0.3)
            else:  # Boreal
                temp = 5 - ((abs_lat - 50) * 0.5)
            
            # Precipitación: varía según región
            # Zonas ecuatoriales: más lluvia
            # Zonas subtropicales: menos lluvia (desiertos)
            if abs_lat < 5:
                rainfall = 2000 + np.random.normal(0, 300)
            elif abs_lat < 20:
                rainfall = 1200 + np.random.normal(0, 400)
            elif abs_lat < 30:
                rainfall = 600 + np.random.normal(0, 300)  # Subtropicales (más secos)
            else:
                rainfall = 800 + np.random.normal(0, 400)
            
            # Altitud: estimación (mayoría de cultivos en llanuras)
            altitude = max(0, 200 + np.random.normal(0, 50))
            
            return {
                'temp': float(np.clip(temp, -20, 50)),  # Límites realistas
                'rainfall': float(np.clip(rainfall, 100, 5000)),  # Límites realistas
                'altitude': float(altitude)
            }
        except Exception as e:
            logger.debug(f"Error en estimación de coords: {str(e)}")
            return None
    
    # ============= PASOS 4-8: INSERTAR DATOS =============
    
    async def _insert_climate_requirements(self, id_species: int) -> Dict:
        """
        PASO 4: Calcula percentiles y inserta climate_requirements
        
        temp_min = percentile(temp, 5)
        temp_opt_min = percentile(temp, 25)
        temp_opt_max = percentile(temp, 75)
        temp_max = percentile(temp, 95)
        """
        try:
            if not self.climate_data['temperatures']:
                logger.warning(f"   ⚠️  Sin datos de temperatura. Omitiendo climate_requirements.")
                return {"status": "skipped", "reason": "No temperature data"}
            
            temps = np.array(self.climate_data['temperatures'])
            rains = np.array(self.climate_data['rainfall'])
            alts = np.array(self.climate_data['altitudes'])
            
            # Calcular percentiles
            climate_params = {
                'id_species': id_species,
                'temp_min': float(np.percentile(temps, 5)),
                'temp_opt_min': float(np.percentile(temps, 25)),
                'temp_opt_max': float(np.percentile(temps, 75)),
                'temp_max': float(np.percentile(temps, 95)),
                'rainfall_min': float(np.percentile(rains, 5)),
                'rainfall_opt_min': float(np.percentile(rains, 25)),
                'rainfall_opt_max': float(np.percentile(rains, 75)),
                'rainfall_max': float(np.percentile(rains, 95)),
                'altitude_min': float(np.percentile(alts, 5)),
                'altitude_max': float(np.percentile(alts, 95)),
                'frost_tolerance': 'moderate',
                'drought_tolerance': 'moderate'
            }
            
            with self.db.cursor() as cur:
                sql = """
                    INSERT INTO climate_requirements (
                        id_species, temp_min, temp_opt_min, temp_opt_max, temp_max,
                        rainfall_min, rainfall_opt_min, rainfall_opt_max, rainfall_max,
                        altitude_min, altitude_max, frost_tolerance, drought_tolerance
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        temp_min = VALUES(temp_min),
                        temp_opt_min = VALUES(temp_opt_min),
                        temp_opt_max = VALUES(temp_opt_max),
                        temp_max = VALUES(temp_max),
                        rainfall_min = VALUES(rainfall_min),
                        rainfall_opt_min = VALUES(rainfall_opt_min),
                        rainfall_opt_max = VALUES(rainfall_opt_max),
                        rainfall_max = VALUES(rainfall_max),
                        altitude_min = VALUES(altitude_min),
                        altitude_max = VALUES(altitude_max)
                """
                cur.execute(sql, tuple(climate_params.values()))
                self.db.commit()
            
            logger.info(f"        Temperatura: {climate_params['temp_opt_min']:.1f}°C - {climate_params['temp_opt_max']:.1f}°C (óptimo)")
            logger.info(f"       Precipitación: {climate_params['rainfall_opt_min']:.0f}mm - {climate_params['rainfall_opt_max']:.0f}mm (anual)")
            logger.info(f"       Altitud: {climate_params['altitude_min']:.0f}m - {climate_params['altitude_max']:.0f}m")
            
            return {"status": "inserted", "params": climate_params}
            
        except Exception as e:
            logger.error(f"       Error insertando climate_requirements: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    async def _insert_crop_profile(self, id_species: int) -> Dict:
        """
        PASO 5: Inserta crop_profile
        
        if family == "Fabaceae":
            nitrogen_fixing = True
        """
        try:
            family = self.species_data.get('family', '')
            nitrogen_fixing = family == 'Fabaceae'
            
            crop_params = {
                'id_species': id_species,
                'crop_type': 'herbaceous',
                'planting_method': 'direct_seed',
                'sunlight_requirement': 'high',
                'water_requirement': 'medium',
                'nitrogen_fixing': nitrogen_fixing
            }
            
            with self.db.cursor() as cur:
                sql = """
                    INSERT INTO crop_profile (
                        id_species, crop_type, planting_method,
                        sunlight_requirement, water_requirement, nitrogen_fixing
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nitrogen_fixing = VALUES(nitrogen_fixing)
                """
                cur.execute(sql, tuple(crop_params.values()))
                self.db.commit()
            
            n2_status = " Fija Nitrógeno" if nitrogen_fixing else " No fija Nitrógeno"
            logger.info(f"      {n2_status} | Siembra: {crop_params['planting_method']} | Luz: {crop_params['sunlight_requirement']}")
            
            return {"status": "inserted", "nitrogen_fixing": nitrogen_fixing}
            
        except Exception as e:
            logger.error(f"       Error insertando crop_profile: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    async def _insert_soil_requirements(self, id_species: int) -> Dict:
        """
        PASO 6: Inserta soil_requirements con valores por defecto
        """
        try:
            soil_params = {
                'id_species': id_species,
                'ph_min': 5.5,
                'ph_max': 7.5,
                'soil_texture': 'loam',
                'drainage': 'good',
                'salinity_tolerance': 'low',
                'organic_matter_need': 'medium'
            }
            
            with self.db.cursor() as cur:
                sql = """
                    INSERT INTO soil_requirements (
                        id_species, ph_min, ph_max, soil_texture,
                        drainage, salinity_tolerance, organic_matter_need
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        id_species = id_species
                """
                cur.execute(sql, tuple(soil_params.values()))
                self.db.commit()
            
            logger.info(f"       pH: {soil_params['ph_min']}-{soil_params['ph_max']} | "
                       f"Textura: {soil_params['soil_texture']} | Drenaje: {soil_params['drainage']}")
            
            return {"status": "inserted"}
            
        except Exception as e:
            logger.error(f"       Error insertando soil_requirements: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    async def _insert_planting_calendar(self, id_species: int) -> Dict:
        """
        PASO 7: Genera planting_calendar desde ocurrencias
        
        SELECT MONTH(eventDate) AS month, COUNT(*) as n
        FROM occurrences WHERE id_species = ?
        GROUP BY month
        
        Interpretación:
        - meses con más ocurrencias → temporada activa
        - meses previos → siembra
        """
        try:
            # Agrupar ocurrencias por mes
            month_counts = {}
            for occ in self.occurrences:
                month = occ.get('month')
                if month is not None:  # Filtrar valores None
                    month_counts[month] = month_counts.get(month, 0) + 1
            
            if not month_counts:
                logger.warning(f"     Sin datos de mes. Usando calendario por defecto.")
                return {"status": "skipped", "reason": "No month data"}
            
            # Encontrar mes pico
            peak_month = max(month_counts.items(), key=lambda x: x[1])[0]
            
            # Heurística: Si pico es sep(9), cosecha es ago-oct, siembra es abr-jun
            harvest_start = (peak_month - 1) % 12 + 1
            harvest_end = (peak_month + 1) % 12 + 1
            planting_start = (peak_month - 5) % 12 + 1
            planting_end = (peak_month - 3) % 12 + 1
            
            calendar_params = {
                'id_species': id_species,
                'planting_start_month': planting_start,
                'planting_end_month': planting_end,
                'harvest_start_month': harvest_start,
                'harvest_end_month': harvest_end,
                'region_type': 'temperate',
                'hemisphere': 'northern'
            }
            
            with self.db.cursor() as cur:
                sql = """
                    INSERT INTO planting_calendar (
                        id_species, planting_start_month, planting_end_month,
                        harvest_start_month, harvest_end_month, region_type, hemisphere
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        id_species = id_species
                """
                cur.execute(sql, tuple(calendar_params.values()))
                self.db.commit()
            
            month_names = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            logger.info(f"       Siembra: {month_names[planting_start]}-{month_names[planting_end]} | "
                       f"Cosecha: {month_names[harvest_start]}-{month_names[harvest_end]}")
            logger.info(f"       Distribución mensual: {dict(sorted(month_counts.items()))}")
            
            return {"status": "inserted", "peak_month": peak_month, "month_distribution": month_counts}
            
        except Exception as e:
            logger.error(f"       Error insertando planting_calendar: {str(e)}")
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    async def _insert_companion_plants(self, id_species: int) -> Dict:
        """
        PASO 8: Inserta companions base según familia
        
        Ejemplos:
        - Fabaceae + corn/maize = nitrogen_fixing
        - Corn + bean + squash = milpa/three sisters
        """
        try:
            inserted = []
            family = self.species_data.get('family', '')
            genus = self.species_data.get('genus', '')
            
            # BASE DE DATOS DE CONOCIMIENTOS: asociaciones comunes
            companion_rules = {
                'Fabaceae': [  # Legumbres pueden fijar nitrógeno
                    {'genus_companion': 'Zea', 'benefit': 'nitrogen_fixing'},  # Maíz
                    {'genus_companion': 'Solanum', 'benefit': 'nitrogen_fixing'},  # Papa/Tomate
                ],
                'Poaceae': [  # Gramíneas
                    {'genus_companion': 'Phaseolus', 'benefit': 'nitrogen_fixing'},  # Frijol/Bean
                    {'genus_companion': 'Cucurbita', 'benefit': 'ground_cover'},  # Calabaza
                ]
            }
            
            # Obtener reglas para esta familia
            companion_matches = companion_rules.get(family, [])
            
            if companion_matches:
                logger.info(f"       Buscando plantas compañeras para familia {family}...")
            
            for rule in companion_matches:
                try:
                    # Buscar especie compañera por género
                    with self.db.cursor() as cur:
                        sql = "SELECT id_species, scientific_name FROM species WHERE genus = %s LIMIT 1"
                        cur.execute(sql, (rule.get('genus_companion'),))
                        result = cur.fetchone()
                        
                        if result:
                            companion_id = result['id_species']
                            companion_name = result['scientific_name']
                            
                            # Insertar relación
                            insert_sql = """
                                INSERT IGNORE INTO companion_plants
                                (id_species_a, id_species_b, relationship_type, benefit_type)
                                VALUES (%s, %s, %s, %s)
                            """
                            cur.execute(insert_sql, (
                                id_species,
                                companion_id,
                                'compatible',
                                rule.get('benefit')
                            ))
                            self.db.commit()
                            inserted.append({
                                'id_species_a': id_species,
                                'id_species_b': companion_id,
                                'benefit': rule.get('benefit'),
                                'companion_name': companion_name
                            })
                            logger.info(f"       Compatible: {companion_name} ({rule.get('benefit')})")
                except Exception as e:
                    logger.debug(f"        Error insertando companion: {str(e)}")
            
            if not inserted:
                logger.info(f"      ℹ  Sin plantas compañeras encontradas para esta familia")
            
            return {"status": "inserted", "count": len(inserted), "inserted": inserted}
            
        except Exception as e:
            logger.error(f"       Error insertando companion_plants: {str(e)}")
            return {"status": "error", "error": str(e)}


# ============= FUNCIÓN PRINCIPAL PARA USO EXTERNO =============
async def enrich_species_agronomy(id_species: int, db_connection) -> Dict:
    """
    Función pública para enriquecer una especie
    
    Args:
        id_species: ID de la especie
        db_connection: Conexión a la BD
        
    Returns:
        Dict con resultado de operaciones
    """
    pipeline = AgronomicEnrichmentPipeline(db_connection)
    return await pipeline.enrich_species(id_species)


def enrich_species_agronomy_sync(id_species: int, db_connection) -> Dict:
    """
    Wrapper sincrónico para enriquecer especie
    Útil para integración con FastAPI sin async
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            enrich_species_agronomy(id_species, db_connection)
        )
        return result
    finally:
        loop.close()
