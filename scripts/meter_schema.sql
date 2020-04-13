-- -----------------------------------------------------
-- Schema meter_tel
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema meter_tel
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `meter_tel` DEFAULT CHARACTER SET utf8 ;
USE `meter_tel` ;

-- -----------------------------------------------------
-- Table `meter_tel`.`address`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`address` (
  `address_id` INT NOT NULL AUTO_INCREMENT,
  `address` VARCHAR(45),
  `address2` VARCHAR(45)
  `district` VARCHAR(45),
  `city` VARCHAR(60),
  `country` VARCHAR(60),
  `postal_code` VARCHAR(45),
  `phone` VARCHAR(45),
  `last_update` TIMESTAMP NOT NULL,
  `location` GEOMETRY,
  PRIMARY KEY (`address_id`),
  UNIQUE INDEX `address_id_UNIQUE` (`address_id` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`service_location`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`service_location` (
  `service_location_id` VARCHAR(45) NOT NULL COMMENT 'Using the service location number as the ID',
  `address_id` INT NOT NULL,
  `map_location` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`service_location_id`),
  UNIQUE INDEX `service_location_id_UNIQUE` (`service_location_id` ASC) VISIBLE,
  INDEX `address_id_idx` (`address_id` ASC) VISIBLE,
  CONSTRAINT `fk_service_location_address_id`
    FOREIGN KEY (`address_id`)
    REFERENCES `meter_tel`.`address` (`address_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`utility`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`utility` (
  `utility_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45),
  `subscription_start` TIMESTAMP NOT NULL,
  `subscription_end` TIMESTAMP NOT NULL,
  PRIMARY KEY (`utility_id`),
  UNIQUE INDEX `utility_id_UNIQUE` (`utility_id` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`meter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`meter` (
  `meter_id` VARCHAR(45) NOT NULL COMMENT 'Meter ID as per AMI Meter ID in rate study',
  `utility_id` INT NOT NULL,
  `service_location_id` VARCHAR(45) NOT NULL,
  `feeder` VARCHAR(45) NOT NULL,
  `substation` VARCHAR(45) NOT NULL,
  `meter_type` VARCHAR(45) NOT NULL COMMENT 'Examples: kWh/Demand, Time-of-Day/kWh/Demand, or AXR-SD (CHANGE TO ENUM)',
  `is_active` BOOLEAN NOT NULL,
  `is_archived` BOOLEAN NOT NULL,
  PRIMARY KEY (`meter_id`, `utility_id`, `service_location_id`),
  UNIQUE INDEX `meter_id_UNIQUE` (`meter_id` ASC) VISIBLE,
  INDEX `service_location_id_idx` (`service_location_id` ASC) VISIBLE,
  INDEX `utility_id_idx` (`utility_id` ASC) VISIBLE,
  CONSTRAINT `fk_meter_service_location_id`
    FOREIGN KEY (`service_location_id`)
    REFERENCES `meter_tel`.`service_location` (`service_location_id`),
  CONSTRAINT `fk_meter_utility_id`
    FOREIGN KEY (`utility_id`)
    REFERENCES `meter_tel`.`utility` (`utility_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`channel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`channel` (
  `channel_id` INT NOT NULL COMMENT 'Given channel number (1 or 3 for HCE). This assumes that channel numbers indicate the same type across many different meters?',
  `meter_id` VARCHAR(45) NOT NULL,
  `utility_id` INT NOT NULL,
  `service_location_id` VARCHAR(45) NOT NULL,
  `type` VARCHAR(45) NOT NULL COMMENT 'Example: forward, or reverse (possible enum with setting?)',
  `setting` INT NOT NULL,
  PRIMARY KEY (`channel_id`),
  UNIQUE INDEX `channel_id_UNIQUE` (`channel_id` ASC) VISIBLE,
  INDEX `meter_id_idx` (`meter_id` ASC) VISIBLE,
  CONSTRAINT `fk_channel_meter_id`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_tel`.`meter` (`meter_id`),
  CONSTRAINT `fk_channel_utility_id`
    FOREIGN KEY(`utility_id`)
    REFERENCES `meter_tel`.`meter` (`utility_id`),
  CONSTRAINT `fk_channel_service_location_id`
    FOREIGN KEY(`service_location_id`)
    REFERENCES `meter_tel`.`meter` (`service_location_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`rate`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`rate` (
  `rate_id` INT NOT NULL AUTO_INCREMENT,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`rate_id`),
  UNIQUE INDEX `tariff_id_UNIQUE` (`rate_id` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `meter_tel`.`interval`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`interval` (
  `interval_id` INT NOT NULL AUTO_INCREMENT,
  `meter_id` VARCHAR(45) NOT NULL,
  `utility_id` 
  `rate_id` INT NOT NULL,
  `status` VARCHAR(45) NULL DEFAULT NULL,
  `start_time` TIMESTAMP NOT NULL,
  `end_time` TIMESTAMP NOT NULL,
  `rate_id` FLOAT NOT NULL,
  PRIMARY KEY (`interval_id`),
  UNIQUE INDEX `reading_id_UNIQUE` (`interval_id` ASC) VISIBLE,
  INDEX `meter_id_idx` (`meter_id` ASC) VISIBLE,
  INDEX `rate_id_idx` (`rate_id` ASC) VISIBLE,
  CONSTRAINT `fk_interval_meter_id`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_tel`.`meter` (`meter_id`),
  CONSTRAINT `fk_interval_utility_id`
    FOREIGN KEY(`utility_id`)
    REFERENCES `meter_tel`.`meter` (`utility_id`),
  CONSTRAINT `fk_interval_service_location_id`
    FOREIGN KEY(`service_location_id`)
    REFERENCES `meter_tel`.`meter` (`service_location_id`),
  CONSTRAINT `fk_interval_rate_id`
    FOREIGN KEY (`rate_id`)
    REFERENCES `meter_tel`.`rate` (`rate_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;