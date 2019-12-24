INSERT INTO `tess`.`system` (`name`) VALUES
	("HCE");
INSERT INTO `tess`.`config` (`system_id`,`name`,`value`) VALUES
	(1,"api-version","1"),
    (1,"mechanism","auction"),
    (1,"interval","300"),
    (1,"time-unit","h"),
    (1,"currency-unit","$"),
    (1,"admin-email","dchassin@slac.stanford.edu");
INSERT INTO `tess`.`resource` (`system_id`,`name`,`quantity_unit`,`price_unit`) VALUES
	(1,"capacity","MW","$/MWh");
INSERT INTO `tess`.`user` (`system_id`,`name`,`email`) VALUES
	(1,"admin","dchassin@slac.stanford.edu"),
	(1,"operator","cbilby@holycross.com");
INSERT INTO `tess`.`device` (`user_id`,`name`) VALUE
	(1,"feeder");
INSERT INTO `tess`.`transaction` (`user_id`,`amount`,`balance`) VALUES
	(1,0,0);
