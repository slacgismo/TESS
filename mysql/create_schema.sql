CREATE SCHEMA IF NOT EXISTS `tess`;
USE `tess`;

#
# Functions
#
# RANDOM_ID() generates a unique_id for tables that require them
CREATE FUNCTION UNIQUE_ID ()
	RETURNS CHAR(32) DETERMINISTIC
    RETURN CONCAT(HEX(RAND()*(~0>>1)),HEX(RAND()*(~0>>1)));
    
#
# Systems
#
# Names of all the system supported by  this TESS instance
#
CREATE TABLE
	IF NOT EXISTS `system` (
		`system_id` INT NOT NULL AUTO_INCREMENT,
		`name` VARCHAR(32) NOT NULL,
		UNIQUE KEY `u_system_name` (`name` ASC),
		PRIMARY KEY (`system_id` ASC)
	)
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Resources
#
# All resources for the current TESS instance.
#
CREATE TABLE
	IF NOT EXISTS `resource` (
		`resource_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `quantity_unit` TEXT NOT NULL,
        `price_unit` TEXT NOT NULL,
        UNIQUE INDEX `u_resource_systemid_name` (`system_id` ASC, `name` ASC),
		CONSTRAINT `fk_resource_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`resource_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    
#
# Users
#
# Users of the current TESS instance.
#
CREATE TABLE
	IF NOT EXISTS `user` (
		`user_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `role` ENUM ('ADMINISTRATOR','OPERATOR','ACCOUNTING','CUSTOMER','TEST') NOT NULL,
        `email` TEXT NOT NULL,
        `sha1pwd` TEXT DEFAULT NULL,
        UNIQUE INDEX `u_user_systemid_name` (`system_id` ASC, `name` ASC),
		CONSTRAINT `fk_user_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`user_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Devices
#
# User devices
#
CREATE TABLE
	IF NOT EXISTS `device` (
		`device_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        UNIQUE INDEX `u_device_deviceid_userid_name` (`device_id` ASC, `user_id` ASC, `name` ASC),
		CONSTRAINT `fk_device_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`device_id` ASC)
   )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Tokens
#
# User access tokens
#
CREATE TABLE
	IF NOT EXISTS `token` (
		`token_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT,
        `unique_id` VARCHAR(32) NOT NULL,
        `is_valid` ENUM ('False','True') DEFAULT 'True',
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE INDEX `u_token_uniqueid` (`unique_id` ASC),
        INDEX `i_token_userid_created` (`user_id` ASC, `created` DESC),
		CONSTRAINT `fk_token_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`token_id` ASC)
    )
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `token_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `token` FOR EACH ROW
		SET NEW.`unique_id` = UNIQUE_ID();


