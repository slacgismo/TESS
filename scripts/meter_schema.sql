-- -----------------------------------------------------
-- Schema meter_telemetry
-- -----------------------------------------------------
CREATE SCHEMA 
  IF NOT EXISTS `meter_telemetry` 
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
  USE `meter_telemetry`;


-- -----------------------------------------------------
-- Table `meter_telemetry`.`meter`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_telemetry`.`meter` (
    `meter_id` VARCHAR(45) NOT NULL COMMENT 'AMI Meter ID in rate study',
    `rate_id` INT NULL COMMENT 'Tariff',
    `service_location_id` VARCHAR(45) NOT NULL,
    `feeder` VARCHAR(45) NOT NULL,
    `substation` VARCHAR(45) NOT NULL,
    `meter_type` VARCHAR(45) NOT NULL COMMENT 'Examples: kWh/Demand, Time-of-Day/kWh/Demand, or AXR-SD',
    PRIMARY KEY (`meter_id`),
    UNIQUE INDEX `meter_id_UNIQUE` (`meter_id` ASC) VISIBLE,
    INDEX `rate_id_idx` (`rate_id` ASC) VISIBLE,
    INDEX `service_location_id_idx` (`service_location_id` ASC) VISIBLE,
    CONSTRAINT `fk_meter_rate_id`
      FOREIGN KEY (`rate_id`)
      REFERENCES `meter_telemetry`.`rate` (`rate_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
    CONSTRAINT `fk_meter_service_location_id`
      FOREIGN KEY (`service_location_id`)
      REFERENCES `meter_telemetry`.`service_location` (`service_location_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_telemetry`.`interval`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_telemetry`.`interval` (
    `interval_id` INT NOT NULL AUTO_INCREMENT,
    `meter_id` VARCHAR(45) NOT NULL,
    `value` FLOAT NOT NULL,
    `status` VARCHAR(45) NULL,
    `start_time` TIMESTAMP NOT NULL,
    `end_time` TIMESTAMP NOT NULL,
    PRIMARY KEY (`interval_id`),
    UNIQUE INDEX `interval_id_UNIQUE` (`interval_id` ASC) VISIBLE,
    INDEX `meter_id_idx` (`meter_id` ASC) VISIBLE,
    CONSTRAINT `fk_interval_meter_id`
      FOREIGN KEY (`meter_id`)
      REFERENCES `meter_telemetry`.`meter` (`meter_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`channel`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_tel`.`channel` (
    `channel_id` INT NOT NULL COMMENT 'Given channel number (1 or 3 for HCE). This assumes that channel numbers indicate the same type across many different meters?',
    `type` VARCHAR(45) NOT NULL COMMENT 'Example: forward, or reverse',
    PRIMARY KEY (`channel_id`),
    UNIQUE INDEX `channel_id_UNIQUE` (`channel_id` ASC) VISIBLE)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`meter_channel`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_telemetry`.`meter_channel` (
    `relationship_id` INT NOT NULL AUTO_INCREMENT,
    `meter_id` VARCHAR(45) NOT NULL,
    `channel_id` INT NOT NULL,
    PRIMARY KEY (`relationship_id`),
    UNIQUE INDEX `relationship_id_UNIQUE` (`relationship_id` ASC) VISIBLE,
    CONSTRAINT `fk_meter_channel_meterid`
      FOREIGN KEY (`meter_id`)
      REFERENCES `meter_telemetry`.`meter` (`meter_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
    CONSTRAINT `fk_meter_channel_channelid`
      FOREIGN KEY (`channel_id`)
      REFERENCES `meter_telemetry`.`channel` (`channel_id`)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`service_location`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_tel`.`service_location` (
    `service_location_id` VARCHAR(45) NOT NULL COMMENT 'Using the service location number as the ID',
    `map_location` VARCHAR(45) NOT NULL,
    `postal_code` VARCHAR(45) NOT NULL,
    PRIMARY KEY (`service_location_id`),
    UNIQUE INDEX `service_location_id_UNIQUE` (`service_location_id` ASC) VISIBLE)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`rate`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_tel`.`rate` (
    `rate_id` INT NOT NULL AUTO_INCREMENT,
    `description` TEXT NOT NULL,
    PRIMARY KEY (`rate_id`),
    UNIQUE INDEX `rate_id_UNIQUE` (`rate_id` ASC) VISIBLE)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `meter_tel`.`schema`
-- -----------------------------------------------------
CREATE TABLE 
  IF NOT EXISTS `meter_tel`.`schema` (
    `attribute` VARCHAR(45) NOT NULL,
    `format` TEXT NOT NULL,
    `description` TEXT NULL,
    `example` TEXT NULL,
    PRIMARY KEY (`attribute`))
  ENGINE = InnoDB;