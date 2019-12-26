INSERT INTO `tess`.`system` (`name`) VALUES
	("HCE");
SET @hce_system_id = LAST_INSERT_ID();
INSERT INTO `tess`.`config` (`system_id`,`name`,`value`) VALUES
	(@hce_system_id,"api-version","1"),
    (@hce_system_id,"mechanism","auction"),
    (@hce_system_id,"interval","300"),
    (@hce_system_id,"time-unit","h"),
    (@hce_system_id,"currency-unit","$"),
    (@hce_system_id,"admin-email","dchassin@slac.stanford.edu");
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(@hce_system_id,"capacity","MW","$/MWh");
INSERT INTO `tess`.`user` (`system_id`,`name`,`email`) VALUES
	(@hce_system_id,"admin","dchassin@slac.stanford.edu");
SET @hce_admin_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`email`) VALUES
	(@hce_system_id,"operator","cbilby@holycross.com");
SET @hce_operator_id = LAST_INSERT_ID();
INSERT INTO `tess`.`device` (`user_id`,`name`) VALUE
	(1,"feeder");
SET @hce_feeder_id = LAST_INSERT_ID();
INSERT INTO `tess`.`setting` (`device_id`,`name`,`value`) VALUE
	(@hce_feeder_id,'capacity_max','1.0 MW'),
    (@hce_feeder_id,'capacity_min','-1.0 MW');
INSERT INTO `tess`.`transaction` (`user_id`,`amount`,`balance`) VALUES
	(@hce_operator_id,0,0);
INSERT INTO `tess`.`token` (`user_id`) VALUES
	(@hce_admin_id),
    (@hce_operator_id);
SELECT * from `tess`.`token`;