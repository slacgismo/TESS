#
# Create HCE system
#
INSERT INTO `tess`.`system` (`name`) VALUES
	("HCE");
SET @hce_system_id = LAST_INSERT_ID();

#
# Define HCE capacity resource
#
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(@hce_system_id,"capacity","MW","$/MWh");
SET @hce_capacity_resource = LAST_INSERT_ID();

#
# Define HCE users `admin` and `operator`
#
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"admin","ADMINISTRATOR","administrator@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_admin_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"operator","OPERATOR","operator@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_operator_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"accounting","ACCOUNTING","accounting@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_accounting_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"testuser1","TEST","testuser1@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_testuser1_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"testuser2","TEST","testuser2@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_testuser2_id = LAST_INSERT_ID();
INSERT INTO `tess`.`user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES
	(@hce_system_id,"testuser3","TEST","testuser3@holycross.com",SHA1('Sl@cG1sm0'));
SET @hce_testuser3_id = LAST_INSERT_ID();

#
# Define primary HCE feeder
#
INSERT INTO `tess`.`device` (`user_id`,`name`) VALUES
	(1,"feeder");
SET @hce_feeder_id = LAST_INSERT_ID();

#
# Set the initial user access tokens
#    
INSERT INTO `tess`.`token` (`user_id`) VALUES
	(@hce_admin_id),
    (@hce_operator_id),
    (@hce_accounting_id),
    (@hce_testuser1_id),
    (@hce_testuser2_id),
    (@hce_testuser3_id);
