-- Crear tablas para enriquecimiento agronómico

-- Tabla de requisitos climáticos
CREATE TABLE IF NOT EXISTS `climate_requirements` (
  `id_climate` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_species` bigint(20) NOT NULL UNIQUE,
  `temp_min` float DEFAULT NULL COMMENT 'Temperatura mínima (5° percentil)',
  `temp_opt_min` float DEFAULT NULL COMMENT 'Temperatura óptima mínima (25° percentil)',
  `temp_opt_max` float DEFAULT NULL COMMENT 'Temperatura óptima máxima (75° percentil)',
  `temp_max` float DEFAULT NULL COMMENT 'Temperatura máxima (95° percentil)',
  `rainfall_min` float DEFAULT NULL COMMENT 'Precipitación mínima (5° percentil)',
  `rainfall_opt_min` float DEFAULT NULL COMMENT 'Precipitación óptima mínima (25° percentil)',
  `rainfall_opt_max` float DEFAULT NULL COMMENT 'Precipitación óptima máxima (75° percentil)',
  `rainfall_max` float DEFAULT NULL COMMENT 'Precipitación máxima (95° percentil)',
  `altitude_min` float DEFAULT NULL COMMENT 'Altitud mínima (5° percentil)',
  `altitude_max` float DEFAULT NULL COMMENT 'Altitud máxima (95° percentil)',
  `frost_tolerance` varchar(50) DEFAULT NULL,
  `drought_tolerance` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_climate`),
  FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de perfil del cultivo
CREATE TABLE IF NOT EXISTS `crop_profile` (
  `id_crop_profile` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_species` bigint(20) NOT NULL UNIQUE,
  `crop_type` varchar(100) DEFAULT 'herbaceous',
  `planting_method` varchar(100) DEFAULT 'direct_seed',
  `sunlight_requirement` varchar(100) DEFAULT 'high',
  `water_requirement` varchar(100) DEFAULT 'medium',
  `nitrogen_fixing` boolean DEFAULT FALSE,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_crop_profile`),
  FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de requisitos de suelo
CREATE TABLE IF NOT EXISTS `soil_requirements` (
  `id_soil_requirement` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_species` bigint(20) NOT NULL UNIQUE,
  `ph_min` float DEFAULT 5.5,
  `ph_max` float DEFAULT 7.5,
  `soil_texture` varchar(100) DEFAULT 'loam',
  `drainage` varchar(100) DEFAULT 'good',
  `salinity_tolerance` varchar(100) DEFAULT 'low',
  `organic_matter_need` varchar(100) DEFAULT 'medium',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_soil_requirement`),
  FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de calendario de siembra
CREATE TABLE IF NOT EXISTS `planting_calendar` (
  `id_planting_calendar` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_species` bigint(20) NOT NULL UNIQUE,
  `planting_start_month` tinyint(4) DEFAULT 1,
  `planting_end_month` tinyint(4) DEFAULT 6,
  `harvest_start_month` tinyint(4) DEFAULT 7,
  `harvest_end_month` tinyint(4) DEFAULT 10,
  `region_type` varchar(100) DEFAULT 'temperate',
  `hemisphere` varchar(20) DEFAULT 'northern',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_planting_calendar`),
  FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de plantas compañeras
CREATE TABLE IF NOT EXISTS `companion_plants` (
  `id_companion` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_species_a` bigint(20) NOT NULL,
  `id_species_b` bigint(20) NOT NULL,
  `relationship_type` varchar(100) DEFAULT 'compatible',
  `benefit_type` varchar(100) DEFAULT NULL COMMENT 'nitrogen_fixing, ground_cover, pest_control, etc.',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_companion`),
  UNIQUE KEY `unique_companion_pair` (`id_species_a`, `id_species_b`),
  FOREIGN KEY (`id_species_a`) REFERENCES `species` (`id_species`),
  FOREIGN KEY (`id_species_b`) REFERENCES `species` (`id_species`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Índices adicionales
CREATE INDEX `idx_climate_species` ON `climate_requirements` (`id_species`);
CREATE INDEX `idx_crop_species` ON `crop_profile` (`id_species`);
CREATE INDEX `idx_soil_species` ON `soil_requirements` (`id_species`);
CREATE INDEX `idx_planting_species` ON `planting_calendar` (`id_species`);
CREATE INDEX `idx_companion_a` ON `companion_plants` (`id_species_a`);
CREATE INDEX `idx_companion_b` ON `companion_plants` (`id_species_b`);
