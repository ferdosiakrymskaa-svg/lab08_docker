SET NAMES utf8mb4;

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO items (name) VALUES ('Пример 1'), ('Пример 2');
