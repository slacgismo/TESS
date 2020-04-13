-- MySQL Script generated by MySQL Workbench
-- Thu Mar 12 11:38:17 2020
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema meter_schema
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `meter_schema` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `meter_schema` ;

-- -----------------------------------------------------
-- Table `meter_schema`.`meter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_schema`.`meter` (
  `meter_id` INT NOT NULL,
  `channel` INT NULL DEFAULT NULL,
  `flow_direction` VARCHAR(45) NULL DEFAULT NULL,
  `service_location` INT NULL DEFAULT NULL,
  `map_location` INT NULL DEFAULT NULL,
  `rate` VARCHAR(45) NULL DEFAULT NULL,
  `substation` VARCHAR(45) NULL DEFAULT NULL,
  `zipcode` INT NULL DEFAULT NULL,
  `feeder` INT NULL DEFAULT NULL,
  `unit` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`meter_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_general_ci;


-- -----------------------------------------------------
-- Table `meter_schema`.`reading`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meter_schema`.`reading` (
  `date` DATE NOT NULL,
  `meter_id` INT NOT NULL,
  `0000` FLOAT NULL,
  `0015` FLOAT NULL,
  `0030` FLOAT NULL,
  `0045` FLOAT NULL,
  `0100` FLOAT NULL,
  `0115` FLOAT NULL,
  `0130` FLOAT NULL,
  `0145` FLOAT NULL,
  `0200` FLOAT NULL,
  `0215` FLOAT NULL,
  `0230` FLOAT NULL,
  `0245` FLOAT NULL,
  `0300` FLOAT NULL,
  `0315` FLOAT NULL,
  `0330` FLOAT NULL,
  `0345` FLOAT NULL,
  `0400` FLOAT NULL,
  `0415` FLOAT NULL,
  `0430` FLOAT NULL,
  `0445` FLOAT NULL,
  `0500` FLOAT NULL,
  `0515` FLOAT NULL,
  `0530` FLOAT NULL,
  `0545` FLOAT NULL,
  `0600` FLOAT NULL,
  `0615` FLOAT NULL,
  `0630` FLOAT NULL,
  `0645` FLOAT NULL,
  `0700` FLOAT NULL,
  `0715` FLOAT NULL,
  `0730` FLOAT NULL,
  `0745` FLOAT NULL,
  `0800` FLOAT NULL,
  `0815` FLOAT NULL,
  `0830` FLOAT NULL,
  `0845` FLOAT NULL,
  `0900` FLOAT NULL,
  `0915` FLOAT NULL,
  `0930` FLOAT NULL,
  `0945` FLOAT NULL,
  `1000` FLOAT NULL,
  `1015` FLOAT NULL,
  `1030` FLOAT NULL,
  `1045` FLOAT NULL,
  `1100` FLOAT NULL,
  `1115` FLOAT NULL,
  `1130` FLOAT NULL,
  `1145` FLOAT NULL,
  `1200` FLOAT NULL,
  `1215` FLOAT NULL,
  `1230` FLOAT NULL,
  `1245` FLOAT NULL,
  `1300` FLOAT NULL,
  `1315` FLOAT NULL,
  `1330` FLOAT NULL,
  `1345` FLOAT NULL,
  `1400` FLOAT NULL,
  `1415` FLOAT NULL,
  `1430` FLOAT NULL,
  `1445` FLOAT NULL,
  `1500` FLOAT NULL,
  `1515` FLOAT NULL,
  `1530` FLOAT NULL,
  `1545` FLOAT NULL,
  `1600` FLOAT NULL,
  `1615` FLOAT NULL,
  `1630` FLOAT NULL,
  `1645` FLOAT NULL,
  `1700` FLOAT NULL,
  `1715` FLOAT NULL,
  `1730` FLOAT NULL,
  `1745` FLOAT NULL,
  `1800` FLOAT NULL,
  `1815` FLOAT NULL,
  `1830` FLOAT NULL,
  `1845` FLOAT NULL,
  `1900` FLOAT NULL,
  `1915` FLOAT NULL,
  `1930` FLOAT NULL,
  `1945` FLOAT NULL,
  `2000` FLOAT NULL,
  `2015` FLOAT NULL,
  `2030` FLOAT NULL,
  `2045` FLOAT NULL,
  `2100` FLOAT NULL,
  `2115` FLOAT NULL,
  `2130` FLOAT NULL,
  `2145` FLOAT NULL,
  `2200` FLOAT NULL,
  `2215` FLOAT NULL,
  `2230` FLOAT NULL,
  `2245` FLOAT NULL,
  `2300` FLOAT NULL,
  `2315` FLOAT NULL,
  `2330` FLOAT NULL,
  `2345` FLOAT NULL,
  INDEX `fk_reading_meter1_idx` (`meter_id` ASC),
  PRIMARY KEY (`date`),
  CONSTRAINT `fk_reading_meter1`
    FOREIGN KEY (`meter_id`)
    REFERENCES `meter_schema`.`meter` (`meter_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_general_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
