-- -----------------------------------------------------
-- Schema meter_tel
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema meter_tel
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `meter_tel` DEFAULT CHARACTER SET utf8 ;
USE `meter_tel` ;

-- -----------------------------------------------------
-- Table `meter_tel`.`rate`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`rate` (
  `rate_id` INT NOT NULL AUTO_INCREMENT,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`rate_id`),
  UNIQUE INDEX `tariff_id_UNIQUE` (`rate_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`country`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`country` (
  `country_id` INT NOT NULL AUTO_INCREMENT,
  `country` VARCHAR(45),
  `last_update` TIMESTAMP,
  PRIMARY KEY (`country_id`),
  UNIQUE INDEX `country_id_UNIQUE` (`country_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`city`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`city` (
  `city_id` INT NOT NULL AUTO_INCREMENT,
  `city` VARCHAR(45),
  `country_id` INT,
  `last_update` TIMESTAMP,
  PRIMARY KEY (`city_id`),
  INDEX `country_id_idx` (`country_id` ASC) VISIBLE,
  CONSTRAINT `fk_city_countryid`
    FOREIGN KEY (`country_id`)
    REFERENCES `meter_tel`.`country` (`country_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`address`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`address` (
  `address_id` INT NOT NULL AUTO_INCREMENT,
  `address` VARCHAR(45),
  `address2` VARCHAR(45),
  `district` VARCHAR(45),
  `city_id` INT,
  `postal_code` VARCHAR(45),
  `phone` VARCHAR(45) NULL,
  `last_update` TIMESTAMP,
  `location` GEOMETRY,
  PRIMARY KEY (`address_id`),
  UNIQUE INDEX `address_id_UNIQUE` (`address_id` ASC) VISIBLE,
  INDEX `city_id_idx` (`city_id` ASC) VISIBLE,
  CONSTRAINT `fk_address_cityid`
    FOREIGN KEY (`city_id`)
    REFERENCES `meter_tel`.`city` (`city_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


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
  CONSTRAINT `fk_service_location_addressid`
    FOREIGN KEY (`address_id`)
    REFERENCES `meter_tel`.`address` (`address_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`utility`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`utility` (
  `utility_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45),
  `subscription_start` TIMESTAMP,
  `subscription_end` TIMESTAMP,
  PRIMARY KEY (`utility_id`),
  UNIQUE INDEX `utility_id_UNIQUE` (`utility_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`meter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`meter` (
  `meter_id` VARCHAR(45) NOT NULL COMMENT 'Meter ID as per AMI Meter ID in rate study',
  `utility_id` INT NOT NULL,
  `service_location_id` VARCHAR(45) NOT NULL,
  `rate_id` INT NULL COMMENT 'Tariff',
  `feeder` VARCHAR(45) NOT NULL,
  `substation` VARCHAR(45) NOT NULL,
  `meter_type` VARCHAR(45) NOT NULL COMMENT 'Examples: kWh/Demand, Time-of-Day/kWh/Demand, or AXR-SD',
  `is_active` BOOLEAN NOT NULL,
  `is_archived` BOOLEAN NOT NULL,
  PRIMARY KEY (`meter_id`),
  UNIQUE INDEX `meter_id_UNIQUE` (`meter_id` ASC) VISIBLE,
  INDEX `rate_id_idx` (`rate_id` ASC) VISIBLE,
  INDEX `service_location_id_idx` (`service_location_id` ASC) VISIBLE,
  INDEX `utility_id_idx` (`utility_id` ASC) VISIBLE,
  CONSTRAINT `fk_meter_rateid`
    FOREIGN KEY (`rate_id`)
    REFERENCES `meter_tel`.`rate` (`rate_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_meter_servicelocationid`
    FOREIGN KEY (`service_location_id`)
    REFERENCES `meter_tel`.`service_location` (`service_location_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_meter_utilityid`
    FOREIGN KEY (`utility_id`)
    REFERENCES `meter_tel`.`utility` (`utility_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`interval`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`interval` (
  `interval_id` INT NOT NULL AUTO_INCREMENT,
  `meter_id` VARCHAR(45) NOT NULL,
  `status` VARCHAR(45) NULL,
  `start_time` TIMESTAMP NOT NULL,
  `end_time` TIMESTAMP NOT NULL,
  `value` FLOAT NOT NULL,
  PRIMARY KEY (`interval_id`),
  UNIQUE INDEX `reading_id_UNIQUE` (`interval_id` ASC) VISIBLE,
  INDEX `meter_id_idx` (`meter_id` ASC) VISIBLE,
  CONSTRAINT `fk_interval_meterid`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_tel`.`meter` (`meter_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`channel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`channel` (
  `channel_id` INT NOT NULL COMMENT 'Given channel number (1 or 3 for HCE). This assumes that channel numbers indicate the same type across many different meters?',
  `type` VARCHAR(45) NOT NULL COMMENT 'Example: forward, or reverse',
  PRIMARY KEY (`channel_id`),
  UNIQUE INDEX `channel_id_UNIQUE` (`channel_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`meter_channel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_tel`.`meter_channel` (
  `relationship_id` INT NOT NULL AUTO_INCREMENT,
  `meter_id` VARCHAR(45) NOT NULL,
  `channel_id` INT NOT NULL,
  PRIMARY KEY (`relationship_id`),
  UNIQUE INDEX `relationship_id_UNIQUE` (`relationship_id` ASC) VISIBLE,
  CONSTRAINT `fk_meter_id`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_tel`.`meter` (`meter_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_channel_id`
    FOREIGN KEY (`channel_id`)
    REFERENCES `meter_tel`.`channel` (`channel_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;