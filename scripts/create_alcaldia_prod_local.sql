-- Script SQL para crear la base de datos `alcaldia_prod` y el usuario local
-- Opción A: todo en el mismo equipo (usuario limitado a 127.0.0.1)
-- Connection name suggested for Navicat: AlcaldiaLocal
-- Reemplaza estos valores si lo deseas. Este script usa las credenciales solicitadas por el usuario:
-- usuario: 'alcaldia'  contraseña: 'admin123'

-- 1) Crear la base de datos con charset utf8mb4 y collation utf8mb4_unicode_ci
CREATE DATABASE IF NOT EXISTS `alcaldia_prod`
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- 2) Crear el usuario (acceso solo desde 127.0.0.1)
CREATE USER IF NOT EXISTS 'alcaldia'@'127.0.0.1' IDENTIFIED BY 'admin123';

-- 3) Otorgar privilegios necesarios para la aplicación (incluye migraciones)
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
  ON `alcaldia_prod`.*
  TO 'alcaldia'@'127.0.0.1';

-- 4) Aplicar cambios
FLUSH PRIVILEGES;

-- IMPORTANTE: Algunas operaciones de migración (constraints/FOREIGN KEY) requieren
-- el privilegio REFERENCES. Si ves un error similar a:
--   "REFERENCES command denied to user 'alcaldia'@'localhost' for table ..."
-- concede también REFERENCES (y considera hacerlo para 'localhost' si tu cliente
-- o Django se conecta como 'alcaldia'@'localhost').

-- Conceder REFERENCES para el mismo usuario en 127.0.0.1 y localhost (útil en Windows):
GRANT REFERENCES ON `alcaldia_prod`.* TO 'alcaldia'@'127.0.0.1';
GRANT REFERENCES ON `alcaldia_prod`.* TO 'alcaldia'@'localhost';
FLUSH PRIVILEGES;

-- Comandos de verificación rápidos (ejecutar después):
-- SHOW DATABASES LIKE 'alcaldia_prod';
-- SHOW GRANTS FOR 'django_user'@'127.0.0.1';

-- Nota: Si tu cliente presenta errores por el plugin de autenticación, usa la variante
-- CREATE USER ... IDENTIFIED WITH mysql_native_password BY '...';
