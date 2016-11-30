CREATE TABLE `navyhack`.`ship_info` (
  `mmsi` INT NOT NULL,
  `name` VARCHAR(255) NULL,
  `flag` VARCHAR(255) NULL,
  `destination` VARCHAR(255) NULL,
  `nav_status` VARCHAR(255) NULL,
  `vessel_type` VARCHAR(255) NULL,
  PRIMARY KEY (`mmsi`));
  