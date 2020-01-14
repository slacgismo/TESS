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

# regular user access to test database
GRANT SELECT,UPDATE,INSERT ON `test`.* TO 'tess'@'localhost';

# all done
FLUSH PRIVILEGES;