#
# Create HCE system
#
INSERT INTO `tess`.`system` (`name`) VALUES
	("HCE");
SET @hce_system_id = LAST_INSERT_ID();

# 
# Create HCE system default configuration
#
INSERT INTO `tess`.`config` (`system_id`,`name`,`value`) VALUES
	(@hce_system_id,"api-version","1"),
    (@hce_system_id,"mechanism","auction"),
    (@hce_system_id,"interval","300"),
    (@hce_system_id,"time-unit","h"),
    (@hce_system_id,"currency-unit","$"),
    (@hce_system_id,"admin-email","dchassin@slac.stanford.edu");

#
# Define HCE capacity resource
#
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(@hce_system_id,"capacity","MW","$/MWh");
SET @hce_capacity_resource = LAST_INSERT_ID();
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(@hce_system_id,"ramping","MW/h","$/MW");
SET @hce_ramping_resource = LAST_INSERT_ID();
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(@hce_system_id,"storage","MWh","$/MWh^2");
SET @hce_storage_resource = LAST_INSERT_ID();

#
# Define HCE users `admin` and `operator`
#
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`) VALUES
	(@hce_system_id,"dchassin","ADMINISTRATOR","dchassin@slac.stanford.edu");
SET @hce_admin_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`) VALUES
	(@hce_system_id,"cbilby","OPERATOR","cbilby@holycross.com");
SET @hce_operator_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`) VALUES
	(@hce_system_id,"cbilby","ACCOUNTING","cbilby@holycross.com");
SET @hce_operator_id = LAST_INSERT_ID();

#
# Define primary HCE feeder
#
INSERT INTO `tess`.`device` (`user_id`,`name`) VALUES
	(1,"feeder");
SET @hce_feeder_id = LAST_INSERT_ID();

#
# Define primary feeder min/max capacity
#
INSERT INTO `tess`.`setting` (`device_id`,`name`,`value`) VALUES
	(@hce_feeder_id,'capacity_max','1.0 MW'),
    (@hce_feeder_id,'capacity_min','-1.0 MW');

#
# Create initial price for capacity resource
#
INSERT INTO `tess`.`price` (`resource_id`,`price`,`quantity`) VALUES
	(@hce_capacity_resource,0.0,0.0);
SET @hce_initial_price_id = LAST_INSERT_ID();

#
# Set the main feeder initial meter reading
#
INSERT INTO `tess`.`meter` (`device_id`,`price_id`,`quantity`) VALUES
	(@hce_feeder_id,@hce_initial_price_id,0.0);
SET @hce_initial_meter_id = LAST_INSERT_ID();

INSERT INTO `tess`.`transaction` (`meter_id`,`amount`,`balance`) VALUES
	(@hce_initial_meter_id,0,0);
    
INSERT INTO `tess`.`token` (`user_id`) VALUES
	(@hce_admin_id),
    (@hce_operator_id);
SELECT * from `tess`.`token`;