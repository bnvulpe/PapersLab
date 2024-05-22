SHOW VARIABLES LIKE "secure_file_priv";

-- Creamos la tabla a poblar `papers` 
CREATE TABLE IF NOT EXISTS papers (
    id INT PRIMARY KEY,
    theme VARCHAR(255),
    month_posted VARCHAR(20),
    day_posted VARCHAR(20),
    publisher VARCHAR(255),
    publisher_description TEXT
);
-- Creamos las tablas temporales para importar los datos de cada .csv independiente
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

-- Poblamos las tablas temporales

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

-- Insertamos los datos en la tabla `papers` a partir de las tablas temporales
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

-- Eliminamos las tablas temporales
DROP TEMPORARY TABLE temp_papers_theme;
DROP TEMPORARY TABLE temp_papers_posted;
DROP TEMPORARY TABLE temp_papers_publisher;

-- Comprobamos que los datos se han insertado correctamente
SELECT * FROM papers;

