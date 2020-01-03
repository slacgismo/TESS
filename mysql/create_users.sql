#
# This script can only be run as root
#

# needed to allow functions to be created by admin
SET GLOBAL log_bin_trust_function_creators = 1;

# admin user
CREATE USER 'tess_a'@'localhost' IDENTIFIED BY 'slacgismo';

# admin user access to TESS database
GRANT ALL ON `tess`.* TO 'tess_a'@'localhost';
REVOKE DROP,DELETE ON `tess`.* FROM 'tess_a'@'localhost';

# admin user access to test database
GRANT ALL ON `test`.* TO 'tess_a'@'localhost';
REVOKE DELETE ON `test`.* FROM 'tess_a'@'localhost';

# regular user
CREATE USER 'tess'@'localhost' IDENTIFIED BY 'slacgismo';

# regular user access to TESS database
GRANT SELECT,UPDATE,INSERT ON `tess`.* TO 'tess'@'localhost';

# cannot revoke these until the tables are created
-- REVOKE INSERT ON `tess`.`config` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`log` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`price` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`resource` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`setting` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`system` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`transaction` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `tess`.`user` FROM 'tess'@'localhost';

# regular user access to test database
GRANT SELECT,UPDATE,INSERT ON `test`.* TO 'tess'@'localhost';

# cannot revoke these until the tables are created
-- REVOKE INSERT ON `test`.`config` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`log` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`price` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`resource` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`setting` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`system` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`transaction` FROM 'tess'@'localhost';
-- REVOKE INSERT ON `test`.`user` FROM 'tess'@'localhost';

# all done
FLUSH PRIVILEGES;