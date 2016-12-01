DROP TABLE IF EXISTS `navyhack`.`ships_last_report_time_view`;
DROP VIEW IF EXISTS `navyhack`.`ships_last_report_time_view`;
CREATE TABLE `navyhack`.`ships_last_report_time_view` (
  `mmsi` INT NOT NULL,
  `reported_time` DATETIME NOT NULL,
  PRIMARY KEY (`mmsi`),
  INDEX `idx_mmsi` (mmsi),
  INDEX `idx_reported_time` (reported_time));
  
  
INSERT INTO ships_last_report_time_view (mmsi, reported_time)
SELECT mmsi, max(reported_time) as max_reported_time
FROM ships_view
GROUP BY mmsi
ON DUPLICATE KEY UPDATE reported_time = max_reported_time;
