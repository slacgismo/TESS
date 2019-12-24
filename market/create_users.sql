CREATE USER 'tess_a'@'localhost' IDENTIFIED BY 'slacgismo';
GRANT SELECT, INSERT, CREATE ON `tess`.* TO 'tess_a'@'localhost';

CREATE USER 'tess'@'localhost' IDENTIFIED BY 'slacgismo';
GRANT SELECT, INSERT ON `tess`.* TO 'tess'@'localhost';
