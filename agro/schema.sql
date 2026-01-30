-- Schema para la base de datos de distribución de especies
-- Este archivo define la estructura de todas las tablas necesarias

-- Tabla de especies
CREATE TABLE IF NOT EXISTS species (
    id_species INT AUTO_INCREMENT PRIMARY KEY,
    taxonKey BIGINT UNIQUE NOT NULL,
    scientific_name VARCHAR(255) NOT NULL,
    phylum VARCHAR(100),
    class_name VARCHAR(100),
    order_name VARCHAR(100),
    family VARCHAR(100),
    genus VARCHAR(100),
    kingdom VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_scientific_name (scientific_name),
    INDEX idx_taxonKey (taxonKey)
);

-- Tabla de zonas ecológicas
CREATE TABLE IF NOT EXISTS ecological_zones (
    id_zone INT AUTO_INCREMENT PRIMARY KEY,
    zone_name VARCHAR(255) NOT NULL,
    biome_type VARCHAR(100),
    climate_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_zone_name (zone_name)
);

-- Tabla de asociación especie-zona
CREATE TABLE IF NOT EXISTS species_zones (
    id_species_zone INT AUTO_INCREMENT PRIMARY KEY,
    id_species INT NOT NULL,
    id_zone INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_species_zone (id_species, id_zone),
    FOREIGN KEY (id_species) REFERENCES species(id_species) ON DELETE CASCADE,
    FOREIGN KEY (id_zone) REFERENCES ecological_zones(id_zone) ON DELETE CASCADE
);

-- Tabla de ocurrencias (observaciones georreferenciadas)
CREATE TABLE IF NOT EXISTS occurrences (
    id_occurrence INT AUTO_INCREMENT PRIMARY KEY,
    gbif_occurrence_id BIGINT UNIQUE NOT NULL,
    id_species INT NOT NULL,
    decimal_latitude DECIMAL(10, 6),
    decimal_longitude DECIMAL(10, 6),
    coordinate_uncertainty_meters INT,
    country VARCHAR(100),
    state_province VARCHAR(100),
    municipality VARCHAR(100),
    locality VARCHAR(255),
    event_date DATE,
    year INT,
    month INT,
    day INT,
    habitat VARCHAR(255),
    elevation INT,
    basis_of_record VARCHAR(50),
    dataset_key VARCHAR(255),
    institution_code VARCHAR(50),
    recorded_by VARCHAR(255),
    identified_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_id_species (id_species),
    INDEX idx_country_state (country, state_province),
    INDEX idx_coordinates (decimal_latitude, decimal_longitude),
    FOREIGN KEY (id_species) REFERENCES species(id_species) ON DELETE CASCADE
);

-- Índices adicionales para queries geoespaciales
CREATE INDEX IF NOT EXISTS idx_occ_coordinates 
ON occurrences (decimal_latitude, decimal_longitude);

CREATE INDEX IF NOT EXISTS idx_occ_location
ON occurrences (country, state_province, municipality);
