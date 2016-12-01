DROP TABLE IF EXISTS `navyhack`.`ships_last_point_view`;
DROP VIEW IF EXISTS `navyhack`.`ships_last_point_view`;
CREATE TABLE `navyhack`.`ships_last_point_view` (
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
  
  
  
INSERT INTO ships_last_point_view (mmsi, reported_time, lat, lon, `class`, course, speed)
SELECT ships_view.mmsi, ships_view.reported_time, lat, lon, `class`, course, speed
from ships_last_report_time_view as lst
join ships_view ON ships_view.mmsi = lst.mmsi and ships_view.reported_time = lst.reported_time
