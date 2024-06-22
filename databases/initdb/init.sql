SHOW VARIABLES LIKE "secure_file_priv";

-- Create the table to be populated `papers` 
CREATE TABLE IF NOT EXISTS papers (
    id INT PRIMARY KEY,
    theme VARCHAR(255),
    month_posted VARCHAR(20),
    day_posted VARCHAR(20),
    publisher VARCHAR(255),
    publisher_description TEXT
);
-- Create temporary tables to import data form each individual .csv file
CREATE TEMPORARY TABLE temp_papers_theme (
    id INT PRIMARY KEY,
    theme VARCHAR(255)
);

CREATE TEMPORARY TABLE temp_papers_posted (
    id INT PRIMARY KEY,
    month_posted VARCHAR(20),
    day_posted VARCHAR(20)
);

CREATE TEMPORARY TABLE temp_papers_publisher (
    id INT PRIMARY KEY,
    publisher VARCHAR(255),
    publisher_description TEXT
);

-- Populate the temporary tables

LOAD DATA INFILE '/var/lib/mysql-files/paper_theme/paper_theme.csv'
INTO TABLE temp_papers_theme
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, theme);

LOAD DATA INFILE '/var/lib/mysql-files/paper_dates/paper_dates.csv'
INTO TABLE temp_papers_posted
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, month_posted, day_posted);

LOAD DATA INFILE '/var/lib/mysql-files/paper_publishers/paper_publishers.csv'
INTO TABLE temp_papers_publisher
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, publisher, publisher_description);

-- Insert data to table `papers` from the temporary tables
INSERT INTO papers (id, theme)
SELECT id, theme FROM temp_papers_theme
ON DUPLICATE KEY UPDATE theme = VALUES(theme);

INSERT INTO papers (id, month_posted, day_posted)
SELECT id, month_posted, day_posted FROM temp_papers_posted
ON DUPLICATE KEY UPDATE 
    month_posted = VALUES(month_posted),
    day_posted = VALUES(day_posted);

INSERT INTO papers (id, publisher, publisher_description)
SELECT id, publisher, publisher_description FROM temp_papers_publisher
ON DUPLICATE KEY UPDATE 
    publisher = VALUES(publisher),
    publisher_description = VALUES(publisher_description);

-- Delete the temporary tables
DROP TEMPORARY TABLE temp_papers_theme;
DROP TEMPORARY TABLE temp_papers_posted;
DROP TEMPORARY TABLE temp_papers_publisher;

-- Show the data in the table `papers` to verify the data was imported
SELECT * FROM papers;

