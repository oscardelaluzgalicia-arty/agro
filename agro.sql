-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 30-01-2026 a las 18:21:28
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `agro`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ecological_zones`
--

CREATE TABLE `ecological_zones` (
  `id_zone` bigint(20) NOT NULL,
  `zone_name` varchar(150) DEFAULT NULL,
  `biome_type` varchar(150) DEFAULT NULL,
  `climate_type` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ecological_zones`
--

INSERT INTO `ecological_zones` (`id_zone`, `zone_name`, `biome_type`, `climate_type`, `description`) VALUES
(1, 'Unknown - Unknown', 'The scientific name for common wheat, the most widely grown type, is Triticum aestivum, belonging to', 'The scientific name for common wheat, the most widely grown type, is Triticum aestivum, belonging to', 'Habitat: The scientific name for common wheat, the most widely grown type, is Triticum aestivum, belonging to, Occurrences: 0'),
(2, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(3, 'Unknown - Unknown', 'Crop of...?', 'Crop of...?', 'Habitat: Crop of...?, Occurrences: 0'),
(4, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(5, 'Unknown - Unknown', 'На обочине дороги\n// on the side of the', 'На обочине дороги\n// on the side of the', 'Habitat: На обочине дороги\n// on the side of the, Occurrences: 0'),
(6, 'Unknown - Unknown', 'A moderate patch within an unsanctioned encampment ', 'A moderate patch within an unsanctioned encampment ', 'Habitat: A moderate patch within an unsanctioned encampment , Occurrences: 0'),
(7, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(8, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(9, 'Unknown - Unknown', 'Frostschäden?', 'Frostschäden?', 'Habitat: Frostschäden?, Occurrences: 0'),
(10, 'Unknown - Unknown', 'ssmtracks', 'ssmtracks', 'Habitat: ssmtracks, Occurrences: 0'),
(11, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(12, 'Unknown - Unknown', 'На обочине дороги\n// on the side of the road', 'На обочине дороги\n// on the side of the road', 'Habitat: На обочине дороги\n// on the side of the road, Occurrences: 0'),
(13, 'Unknown - Unknown', 'cat grass seed', 'cat grass seed', 'Habitat: cat grass seed, Occurrences: 0'),
(14, 'Unknown - Unknown', 'Put out birdseed and it got rained on and now there’s a bunch of sprouts in there lol.', 'Put out birdseed and it got rained on and now there’s a bunch of sprouts in there lol.', 'Habitat: Put out birdseed and it got rained on and now there’s a bunch of sprouts in there lol., Occurrences: 0'),
(15, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(16, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(17, 'Unknown - Unknown', 'Found in the same yard as several sorghum plants, likely left over from birdseed', 'Found in the same yard as several sorghum plants, likely left over from birdseed', 'Habitat: Found in the same yard as several sorghum plants, likely left over from birdseed, Occurrences: 0'),
(18, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(19, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(20, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(21, 'Unknown - Unknown', 'Growing in the gutter - bird spread?', 'Growing in the gutter - bird spread?', 'Habitat: Growing in the gutter - bird spread?, Occurrences: 0'),
(22, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(23, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(24, 'Unknown - Unknown', 'Left side.', 'Left side.', 'Habitat: Left side., Occurrences: 0'),
(25, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(26, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(27, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(28, 'Unknown - Unknown', 'Wheat seeds brought in with a truck load of road gravel', 'Wheat seeds brought in with a truck load of road gravel', 'Habitat: Wheat seeds brought in with a truck load of road gravel, Occurrences: 0'),
(29, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(30, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(31, 'Unknown - Unknown', 'На обочине дороги\n// on the side of the road', 'На обочине дороги\n// on the side of the road', 'Habitat: На обочине дороги\n// on the side of the road, Occurrences: 0'),
(32, 'Unknown - Unknown', 'See bird   https://www.inaturalist.org/observations/326213758', 'See bird   https://www.inaturalist.org/observations/326213758', 'Habitat: See bird   https://www.inaturalist.org/observations/326213758, Occurrences: 0'),
(33, 'Unknown - Unknown', 'Not cultivated', 'Not cultivated', 'Habitat: Not cultivated, Occurrences: 0'),
(34, 'Unknown - Unknown', 'گندم🌾', 'گندم🌾', 'Habitat: گندم🌾, Occurrences: 0'),
(35, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(36, 'Unknown - Unknown', 'Not in cultivation, only a singular plant', 'Not in cultivation, only a singular plant', 'Habitat: Not in cultivation, only a singular plant, Occurrences: 0'),
(37, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(38, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(39, 'Unknown - Unknown', 'trigo (Triticum aestivum; Poaceae), com as espigas quase prontas para a colheita.\nErva exótica, prov', 'trigo (Triticum aestivum; Poaceae), com as espigas quase prontas para a colheita.\nErva exótica, prov', 'Habitat: trigo (Triticum aestivum; Poaceae), com as espigas quase prontas para a colheita.\nErva exótica, prov, Occurrences: 0'),
(40, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(41, 'Unknown - Unknown', 'Заброшенное поле.', 'Заброшенное поле.', 'Habitat: Заброшенное поле., Occurrences: 0'),
(42, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(43, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(44, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(45, 'Unknown - Unknown', 'App\'s suggestion!?\nBusy street, near sidewalk', 'App\'s suggestion!?\nBusy street, near sidewalk', 'Habitat: App\'s suggestion!?\nBusy street, near sidewalk, Occurrences: 0'),
(46, 'Unknown - Unknown', 'On edge of new gravel pathway', 'On edge of new gravel pathway', 'Habitat: On edge of new gravel pathway, Occurrences: 0'),
(47, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(48, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(49, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(50, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(51, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(52, 'Unknown - Unknown', ' -117.16', ' -117.16', 'Habitat:  -117.16, Occurrences: 0'),
(53, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0'),
(54, 'Unknown - Unknown', '', '', 'Habitat: , Occurrences: 0');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modules`
--

CREATE TABLE `modules` (
  `id_module` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `occurrences`
--

CREATE TABLE `occurrences` (
  `id_occurrence` bigint(20) NOT NULL,
  `gbif_occurrence_id` bigint(20) DEFAULT NULL,
  `id_species` bigint(20) NOT NULL,
  `decimal_latitude` decimal(10,7) DEFAULT NULL,
  `decimal_longitude` decimal(10,7) DEFAULT NULL,
  `coordinate_uncertainty_meters` float DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `state_province` varchar(100) DEFAULT NULL,
  `municipality` varchar(100) DEFAULT NULL,
  `locality` text DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `year` smallint(6) DEFAULT NULL,
  `month` tinyint(4) DEFAULT NULL,
  `day` tinyint(4) DEFAULT NULL,
  `habitat` text DEFAULT NULL,
  `elevation` float DEFAULT NULL,
  `basis_of_record` varchar(50) DEFAULT NULL,
  `dataset_key` varchar(100) DEFAULT NULL,
  `institution_code` varchar(100) DEFAULT NULL,
  `recorded_by` varchar(255) DEFAULT NULL,
  `identified_by` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persons`
--

CREATE TABLE `persons` (
  `id_person` bigint(20) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `age` tinyint(4) DEFAULT NULL,
  `email` varchar(150) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `persons`
--

INSERT INTO `persons` (`id_person`, `full_name`, `age`, `email`, `created_at`) VALUES
(1, 'prueba', 27, 'prueba@test', '2026-01-28 01:45:21');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `species`
--

CREATE TABLE `species` (
  `id_species` bigint(20) NOT NULL,
  `taxonKey` bigint(20) NOT NULL,
  `scientific_name` varchar(255) NOT NULL,
  `kingdom` varchar(100) DEFAULT NULL,
  `phylum` varchar(100) DEFAULT NULL,
  `class_name` varchar(100) DEFAULT NULL,
  `order_name` varchar(100) DEFAULT NULL,
  `family` varchar(100) DEFAULT NULL,
  `genus` varchar(100) DEFAULT NULL,
  `species` varchar(100) DEFAULT NULL,
  `taxonomic_status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `species`
--

INSERT INTO `species` (`id_species`, `taxonKey`, `scientific_name`, `kingdom`, `phylum`, `class_name`, `order_name`, `family`, `genus`, `species`, `taxonomic_status`, `created_at`) VALUES
(1, 206097367, 'Zea mays', 'Plantae', NULL, NULL, NULL, NULL, NULL, 'Zea mays', 'ACCEPTED', '2026-01-28 04:40:34'),
(2, 145956043, 'Oryza sativa', 'Plantae', 'Angiospermae', 'Liliopsida', 'Poales', 'Poaceae', 'Oryza', 'Oryza sativa', 'ACCEPTED', '2026-01-28 23:11:53'),
(3, 143611484, 'Triticum aestivum', 'Plantae', 'Tracheophyta', 'Liliopsida', 'Poales', 'Poaceae', 'Triticum', 'Triticum aestivum', 'ACCEPTED', '2026-01-28 23:28:17'),
(4, 191954299, 'Solanum lycopersicum', 'Plantae', 'Trachaeophyta', 'Magnoliopsida', 'Solanales', 'Solanaceae', 'Solanum', 'Solanum lycopersicum', 'ACCEPTED', '2026-01-28 23:45:51');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `species_interactions`
--

CREATE TABLE `species_interactions` (
  `id_interaction` bigint(20) NOT NULL,
  `id_species` bigint(20) NOT NULL,
  `related_id_species` bigint(20) NOT NULL,
  `interaction_type` enum('herbivore','pathogen','pollinator','symbiotic','parasite','predator') DEFAULT NULL,
  `confidence_level` enum('low','medium','high') DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  `methodology` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `species_zones`
--

CREATE TABLE `species_zones` (
  `id_species` bigint(20) NOT NULL,
  `id_zone` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id_user` bigint(20) NOT NULL,
  `id_person` bigint(20) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `status` enum('active','inactive','blocked') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id_user`, `id_person`, `username`, `password_hash`, `status`, `created_at`) VALUES
(1, 1, 'arty', '$2b$12$TXORgiPj.3LI63Pv5VxCi.c.BnEXOI7pjsP77S1vmsfXXct74UuyK', 'active', '2026-01-28 01:46:01');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_modules`
--

CREATE TABLE `user_modules` (
  `id_user` bigint(20) NOT NULL,
  `id_module` bigint(20) NOT NULL,
  `access_level` enum('read','write','admin') DEFAULT 'read',
  `granted_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vernacular_names`
--

CREATE TABLE `vernacular_names` (
  `id_vernacular` bigint(20) NOT NULL,
  `id_species` bigint(20) NOT NULL,
  `language` varchar(50) DEFAULT NULL,
  `common_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `ecological_zones`
--
ALTER TABLE `ecological_zones`
  ADD PRIMARY KEY (`id_zone`);

--
-- Indices de la tabla `modules`
--
ALTER TABLE `modules`
  ADD PRIMARY KEY (`id_module`);

--
-- Indices de la tabla `occurrences`
--
ALTER TABLE `occurrences`
  ADD PRIMARY KEY (`id_occurrence`),
  ADD UNIQUE KEY `gbif_occurrence_id` (`gbif_occurrence_id`),
  ADD KEY `idx_occ_species` (`id_species`),
  ADD KEY `idx_occ_coords` (`decimal_latitude`,`decimal_longitude`),
  ADD KEY `idx_occ_country` (`country`),
  ADD KEY `idx_occ_date` (`event_date`);

--
-- Indices de la tabla `persons`
--
ALTER TABLE `persons`
  ADD PRIMARY KEY (`id_person`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `species`
--
ALTER TABLE `species`
  ADD PRIMARY KEY (`id_species`),
  ADD UNIQUE KEY `taxonKey` (`taxonKey`),
  ADD KEY `idx_species_taxonkey` (`taxonKey`);

--
-- Indices de la tabla `species_interactions`
--
ALTER TABLE `species_interactions`
  ADD PRIMARY KEY (`id_interaction`),
  ADD KEY `id_species` (`id_species`),
  ADD KEY `related_id_species` (`related_id_species`);

--
-- Indices de la tabla `species_zones`
--
ALTER TABLE `species_zones`
  ADD PRIMARY KEY (`id_species`,`id_zone`),
  ADD KEY `id_zone` (`id_zone`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_users_person` (`id_person`);

--
-- Indices de la tabla `user_modules`
--
ALTER TABLE `user_modules`
  ADD PRIMARY KEY (`id_user`,`id_module`),
  ADD KEY `idx_um_user` (`id_user`),
  ADD KEY `idx_um_module` (`id_module`);

--
-- Indices de la tabla `vernacular_names`
--
ALTER TABLE `vernacular_names`
  ADD PRIMARY KEY (`id_vernacular`),
  ADD KEY `id_species` (`id_species`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `ecological_zones`
--
ALTER TABLE `ecological_zones`
  MODIFY `id_zone` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT de la tabla `modules`
--
ALTER TABLE `modules`
  MODIFY `id_module` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `occurrences`
--
ALTER TABLE `occurrences`
  MODIFY `id_occurrence` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `persons`
--
ALTER TABLE `persons`
  MODIFY `id_person` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `species`
--
ALTER TABLE `species`
  MODIFY `id_species` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `species_interactions`
--
ALTER TABLE `species_interactions`
  MODIFY `id_interaction` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id_user` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `vernacular_names`
--
ALTER TABLE `vernacular_names`
  MODIFY `id_vernacular` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `occurrences`
--
ALTER TABLE `occurrences`
  ADD CONSTRAINT `occurrences_ibfk_1` FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`);

--
-- Filtros para la tabla `species_interactions`
--
ALTER TABLE `species_interactions`
  ADD CONSTRAINT `species_interactions_ibfk_1` FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`),
  ADD CONSTRAINT `species_interactions_ibfk_2` FOREIGN KEY (`related_id_species`) REFERENCES `species` (`id_species`);

--
-- Filtros para la tabla `species_zones`
--
ALTER TABLE `species_zones`
  ADD CONSTRAINT `species_zones_ibfk_1` FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`),
  ADD CONSTRAINT `species_zones_ibfk_2` FOREIGN KEY (`id_zone`) REFERENCES `ecological_zones` (`id_zone`);

--
-- Filtros para la tabla `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`id_person`) REFERENCES `persons` (`id_person`);

--
-- Filtros para la tabla `user_modules`
--
ALTER TABLE `user_modules`
  ADD CONSTRAINT `user_modules_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`),
  ADD CONSTRAINT `user_modules_ibfk_2` FOREIGN KEY (`id_module`) REFERENCES `modules` (`id_module`);

--
-- Filtros para la tabla `vernacular_names`
--
ALTER TABLE `vernacular_names`
  ADD CONSTRAINT `vernacular_names_ibfk_1` FOREIGN KEY (`id_species`) REFERENCES `species` (`id_species`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
