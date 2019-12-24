#
# Database
#
CREATE DATABASE 
	IF NOT EXISTS `tess` 
	DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

#
# Functions
#
DROP FUNCTION IF EXISTS `tess`.RANDOM_ID;
CREATE FUNCTION `tess`.RANDOM_ID ()
	RETURNS CHAR(32) DETERMINISTIC
    RETURN CONCAT(HEX(RAND()*(~0>>1)),HEX(RAND()*(~0>>1)));
    
#
# Systems
#
# Names of all the system supported by  this TESS instance
#
CREATE TABLE
	IF NOT EXISTS `tess`.`system` (
		`system_id` INT NOT NULL AUTO_INCREMENT,
		`name` VARCHAR(32) NOT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE KEY `u_system_name` (`name` ASC),
		PRIMARY KEY (`system_id` ASC)
	)
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Config
#
# All the configuration parameters of the current TESS instance.
#
CREATE TABLE
	IF NOT EXISTS `tess`.`config` (
		`config_id` INT NOT NULL AUTO_INCREMENT,
		`system_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE KEY `u_config_systemid_name_created` (`system_id` ASC,`name` ASC,`created` DESC),
		CONSTRAINT `fk_config_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
		PRIMARY KEY (`config_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Resources
#
# All resources for the current TESS instance.
#
CREATE TABLE
	IF NOT EXISTS `tess`.`resource` (
		`resource_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `quantity_unit` TEXT NOT NULL,
        `price_unit` TEXT NOT NULL,
        `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY `u_resource_systemid_name_created` (`system_id` ASC, `name` ASC, `created` DESC),
		CONSTRAINT `fk_resource_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE RESTRICT 
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
	IF NOT EXISTS `tess`.`user` (
		`user_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `email` TEXT NOT NULL,
        `sha1pwd` TEXT DEFAULT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_user_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`user_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Preferences
#
# User preferences
#
CREATE TABLE
	IF NOT EXISTS `tess`.`preference` (
		`preference_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE KEY `u_preference_userid_name_created` (`user_id` ASC,`name` ASC,`created` DESC),
		CONSTRAINT `fk_preference_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`preference_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Devices
#
# User devices
#
CREATE TABLE
	IF NOT EXISTS `tess`.`device` (
		`device_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `unique_id` VARCHAR(32) NOT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE INDEX `u_device_uniqueid` (`unique_id` ASC),
		CONSTRAINT `fk_device_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`device_id` ASC)
   )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `tess`.`device_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `tess`.`device` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();

#
# Settings
#
# Device settings
#
CREATE TABLE
	IF NOT EXISTS `tess`.`setting` (
		`setting_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE KEY `u_setting_deviceid_name_created` (`device_id` ASC,`name` ASC,`created` DESC),
		CONSTRAINT `fk_setting_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`setting_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


#
# Orders
#
# Device resource orders
#
CREATE TABLE
	IF NOT EXISTS `tess`.`order` (
        `order_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
        `unique_id` VARCHAR(32) NOT NULL,
        `resource_id` INT NOT NULL,
        `quantity` DECIMAL(8,3) NOT NULL COMMENT "ask/sell<0, offer/buy>0, =0 is invalid",
        `price` DECIMAL(8,3) COMMENT "<0 is invalid",
        `current` DECIMAL(8,3) COMMENT "NULL if current=quantity",
        `duration` DECIMAL(8,3) COMMENT "only used for orderbook mechanism",
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE INDEX `u_order_uniqueid` (`unique_id` ASC),
		CONSTRAINT `fk_order_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
		CONSTRAINT `fk_order_resourceid` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`order_id` ASC)
   )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `tess`.`order_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `tess`.`order` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();

#
# Prices
#
# Clearing prices
#
CREATE TABLE
	IF NOT EXISTS `tess`.`price` (
		`price_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `resource_id` INT NOT NULL,
        `price` DECIMAL(8,3) NOT NULL,
        `quantity` DECIMAL(8,3) NOT NULL,
        `margin` DECIMAL(8,3),
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE KEY `u_price_priceid_systemid_created` (`price_id` ASC,`system_id` ASC,`created` DESC),
		CONSTRAINT `fk_price_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
		CONSTRAINT `fk_price_resourceid` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`price_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Meters
#
# Device resource metering
#
CREATE TABLE
	IF NOT EXISTS `tess`.`meter` (
		`meter_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
        `resource_id` INT NOT NULL,
        `price_id` INT NOT NULL,
        `quantity` DECIMAL(8,3) NOT NULL COMMENT "ask/sell<0, offer/buy>0, =0 is invalid",
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_meter_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
		CONSTRAINT `fk_meter_resourceid` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
		UNIQUE INDEX `u_meter_deviceid_resourceid` (`device_id` ASC, `resource_id` ASC),
		PRIMARY KEY (`meter_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    

#
# Accounts
#
# User accounts
#
CREATE TABLE
	IF NOT EXISTS `tess`.`transaction` (
		`transaction_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT,
        `amount` DECIMAL(8,3),
        `balance` DECIMAL(8,3),
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX `i_userid_created` (`user_id` ASC, `created` DESC),
        PRIMARY KEY (`transaction_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Tokens
#
# User access tokens
#
CREATE TABLE
	IF NOT EXISTS `tess`.`token` (
		`transaction_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT,
        `unique_id` VARCHAR(32) NOT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_token_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE RESTRICT 
            ON UPDATE RESTRICT,
        UNIQUE INDEX `u_token_uniqueid` (`unique_id` ASC),
        INDEX `i_token_userid_created` (`user_id` ASC, `created` DESC),
        PRIMARY KEY (`transaction_id` ASC)
    )
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `tess`.`token_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `tess`.`token` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();
