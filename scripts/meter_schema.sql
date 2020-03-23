SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema meter_telemetry
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `meter_telemetry` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `meter_telemetry` ;

-- -----------------------------------------------------
-- Table `meter_telemetry`.`meter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_telemetry`.`meter` (
  `meter_id` INT(11) NOT NULL,
  `channel` INT(11) NULL DEFAULT NULL,
  `flow_direction` VARCHAR(45) NULL DEFAULT NULL,
  `service_location` INT(11) NULL DEFAULT NULL,
  `map_location` INT(11) NULL DEFAULT NULL,
  `rate` VARCHAR(45) NULL DEFAULT NULL,
  `substation` VARCHAR(45) NULL DEFAULT NULL,
  `zipcode` INT(11) NULL DEFAULT NULL,
  `feeder` INT(11) NULL DEFAULT NULL,
  `unit` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`meter_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `meter_telemetry`.`reading`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_telemetry`.`reading` (
  `reading_id` INT(11) NOT NULL AUTO_INCREMENT,
  `meter_id` INT(11) NOT NULL,
  `start_time` TIME NULL DEFAULT NULL,
  `end_time` TIME NULL DEFAULT NULL,
  `date` DATE NOT NULL,
  `value` FLOAT UNSIGNED ZEROFILL NULL DEFAULT NULL,
  PRIMARY KEY (`reading_id`),
  UNIQUE INDEX `reading_id_UNIQUE` (`reading_id` ASC),
  INDEX `meter_id_idx` (`meter_id` ASC),
  CONSTRAINT `meter_id`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_telemetry`.`meter` (`meter_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;