#
# Functions
#
# RANDOM_ID() generates a unique_id for tables that require them
CREATE FUNCTION RANDOM_ID ()
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
	IF NOT EXISTS `config` (
		`config_id` INT NOT NULL AUTO_INCREMENT,
		`system_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_config_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE CASCADE 
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
	IF NOT EXISTS `resource` (
		`resource_id` INT NOT NULL AUTO_INCREMENT,
        `system_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `quantity_unit` TEXT NOT NULL,
        `price_unit` TEXT NOT NULL,
        `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
        `role` ENUM ('ADMINISTRATOR','OPERATOR','ACCOUNTING','CUSTOMER') NOT NULL,
        `email` TEXT NOT NULL,
        `sha1pwd` TEXT DEFAULT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_user_systemid` FOREIGN KEY (`system_id`) REFERENCES `system` (`system_id`) 
            ON DELETE CASCADE 
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
	IF NOT EXISTS `preference` (
		`preference_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_preference_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE CASCADE 
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
	IF NOT EXISTS `device` (
		`device_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT NOT NULL,
        `name` VARCHAR(32) NOT NULL,
        `unique_id` VARCHAR(32) NOT NULL,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE INDEX `u_device_uniqueid` (`unique_id` ASC),
		CONSTRAINT `fk_device_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`device_id` ASC)
   )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `device_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `device` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();

#
# Settings
#
# Device settings
#
CREATE TABLE
	IF NOT EXISTS `setting` (
		`setting_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
		`name` VARCHAR(32) NOT NULL,
		`value` TEXT,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_setting_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`setting_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


#
# Prices
#
# Clearing prices
#
CREATE TABLE
	IF NOT EXISTS `price` (
		`price_id` INT NOT NULL AUTO_INCREMENT,
        `resource_id` INT NOT NULL,
        `price` DOUBLE NOT NULL,
        `quantity` DOUBLE NOT NULL,
        `margin` DOUBLE,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_price_resourceid` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        PRIMARY KEY (`price_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#
# Orders
#
# Device resource orders
#
CREATE TABLE
	IF NOT EXISTS `order` (
        `order_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
        `unique_id` VARCHAR(32) NOT NULL,
        `resource_id` INT NOT NULL,
        `quantity` DOUBLE NOT NULL COMMENT "ask/sell<0, offer/buy>0, =0 is invalid",
        `bid` DOUBLE COMMENT "<0 is invalid",
        `current` DOUBLE COMMENT "NULL if current=quantity",
        `duration` DOUBLE COMMENT "only used for orderbook mechanism",
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `price_id` INT,
        `closed` TIMESTAMP,
        UNIQUE INDEX `u_order_uniqueid` (`unique_id` ASC),
		CONSTRAINT `fk_order_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
		CONSTRAINT `fl_order_priceid` FOREIGN KEY (`price_id`) REFERENCES `price` (`price_id`)
			ON DELETE CASCADE
            ON UPDATE RESTRICT,
		CONSTRAINT `fk_order_resourceid` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
         PRIMARY KEY (`order_id` ASC)
   )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `order_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `order` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = CURRENT_USER 
    SQL SECURITY DEFINER
VIEW `order_state` AS
    SELECT 
        `order`.`order_id` AS `order_id`,
        `order`.`device_id` AS `device_id`,
        `order`.`unique_id` AS `unique_id`,
        `order`.`resource_id` AS `resource_id`,
        `order`.`quantity` AS `quantity`,
        `order`.`bid` AS `bid`,
        `order`.`current` AS `current`,
        `order`.`duration` AS `duration`,
        `order`.`created` AS `created`,
        `order`.`price_id` AS `price_id`,
        `order`.`closed` AS `closed`,
        (CASE
            WHEN
                (ISNULL(`order`.`price_id`)
                    AND (ISNULL(`order`.`closed`)
                    OR (`order`.`closed` > NOW())))
            THEN
                'NEW'
            WHEN
                (NOT ISNULL(`order`.`price_id`)
                    AND (ISNULL(`order`.`closed`)
                    OR (`order`.`closed` > NOW())))
            THEN
                'OPEN'
            WHEN
                (NOT ISNULL(`order`.`price_id`)
                    AND (`order`.`closed` <= NOW()))
            THEN
                'CLOSED'
            WHEN
                (ISNULL(`order`.`price_id`)
                    AND (`order`.`closed` <= NOW()))
            THEN
                'DELETED'
            ELSE 'INVALID'
        END) AS `state`
    FROM
        `order`;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = CURRENT_USER 
    SQL SECURITY DEFINER
VIEW `order_status` AS
    SELECT 
        `order_state`.`order_id` AS `order_id`,
        `order_state`.`device_id` AS `device_id`,
        `order_state`.`unique_id` AS `unique_id`,
        `order_state`.`resource_id` AS `resource_id`,
        `order_state`.`quantity` AS `quantity`,
        `order_state`.`bid` AS `bid`,
        `order_state`.`current` AS `current`,
        `order_state`.`duration` AS `duration`,
        `order_state`.`created` AS `created`,
        `order_state`.`price_id` AS `price_id`,
        `order_state`.`closed` AS `closed`,
        `order_state`.`state` AS `state`,
        IF((`order_state`.`quantity` < 0),
            (`price`.`price` >= `order_state`.`bid`),
            (`price`.`price` <= `order_state`.`bid`)) AS `status`,
        `price`.`margin` AS `margin`
    FROM
        (`order_state`
        JOIN `price` ON ((`order_state`.`price_id` = `price`.`price_id`)))
    WHERE
        (`order_state`.`state` = 'OPEN');
#
# Meters
#
# Device resource metering
#
CREATE TABLE
	IF NOT EXISTS `meter` (
		`meter_id` INT NOT NULL AUTO_INCREMENT,
        `device_id` INT NOT NULL,
        `price_id` INT NOT NULL,
        `quantity` DOUBLE NOT NULL COMMENT "produce<0, consume>0, =0 is invalid",
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_meter_deviceid` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
		CONSTRAINT `fk_meter_priceid` FOREIGN KEY (`price_id`) REFERENCES `price` (`price_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
		UNIQUE INDEX `u_meter_deviceid_priceid_created` (`device_id` ASC, `price_id` ASC,`created` ASC),
		PRIMARY KEY (`meter_id` ASC)
    )
    ENGINE=InnoDB 
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    

#
# Transactions
#
# User transactions
#
CREATE TABLE
	IF NOT EXISTS `transaction` (
		`transaction_id` INT NOT NULL AUTO_INCREMENT,
        `meter_id` INT,
        `amount` DOUBLE,
        `balance` DOUBLE,
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 		CONSTRAINT `fk_transaction_meterid` FOREIGN KEY (`meter_id`) REFERENCES `meter` (`meter_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
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
	IF NOT EXISTS `token` (
		`token_id` INT NOT NULL AUTO_INCREMENT,
        `user_id` INT,
        `unique_id` VARCHAR(32) NOT NULL,
        `is_valid` ENUM ('False','True') DEFAULT 'True',
		`created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT `fk_token_userid` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) 
            ON DELETE CASCADE 
            ON UPDATE RESTRICT,
        UNIQUE INDEX `u_token_uniqueid` (`unique_id` ASC),
        INDEX `i_token_userid_created` (`user_id` ASC, `created` DESC),
        PRIMARY KEY (`token_id` ASC)
    )
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE 
	DEFINER = CURRENT_USER 
	TRIGGER `token_BEFORE_INSERT_1` 
	BEFORE INSERT 
	ON `token` FOR EACH ROW
		SET NEW.`unique_id` = RANDOM_ID();

#
# Logs
#
# Log messages
#
CREATE TABLE
    IF NOT EXISTS `log` (
        `log_id` INT NOT NULL AUTO_INCREMENT,
        `message` TEXT NOT NULL,
        `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX `i_log_created` (`created` DESC),
        PRIMARY KEY (`log_id` ASC)
    )
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
INSERT INTO `log` (`message`) VALUES ('Database created');

