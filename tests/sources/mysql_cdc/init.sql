CREATE TABLE test_db.test_table (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    value INT NOT NULL
);
INSERT INTO test_db.test_table VALUES (0, 'preexisting', 0);
CREATE USER 'cdc'@'%' IDENTIFIED BY 'cdc_password';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc'@'%';
GRANT SELECT ON test_db.test_table TO 'cdc'@'%';
