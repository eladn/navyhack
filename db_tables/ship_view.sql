DROP TABLE IF EXISTS `navyhack`.`ships_view`;
DROP VIEW IF EXISTS `navyhack`.`ships_view`;
CREATE TABLE `navyhack`.`ships_view` (
  `mmsi` INT NOT NULL,
  `reported_time` DATETIME NOT NULL,
  `lat` FLOAT NOT NULL,
  `lon` FLOAT NOT NULL,
  `class` VARCHAR(63) NOT NULL,
  `course` FLOAT NOT NULL,
  `speed` FLOAT NOT NULL,
  PRIMARY KEY (`mmsi`, `reported_time`),
  INDEX `idx_ship_tracks_lat_lon` (lat, lon),
  INDEX `idx_mmsi` (mmsi),
  INDEX `idx_reported_time` (reported_time));
  
  
  
INSERT INTO ships_view (mmsi, reported_time, lat, lon, `class`, course, speed)
SELECT ship_tracks.mmsi, reported_time, lat, lon, COALESCE(ship_type.ship_type, 'Other') as `class`, course, speed
from ship_tracks
left join ship_info on ship_tracks.mmsi = ship_info.mmsi
left join vessel_type_to_ship_type as ship_type on ship_type.vessel_type = ship_info.vessel_type;
