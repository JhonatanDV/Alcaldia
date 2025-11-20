-- Script para verificar y convertir tablas a InnoDB
-- Base de datos: maintenance_db
-- Fecha: 2025-11-20

-- 1. Verificar el motor de almacenamiento por defecto
SELECT @@default_storage_engine AS 'Motor por Defecto';

-- 2. Verificar los motores disponibles
SHOW ENGINES;

-- 3. Listar todas las tablas y sus motores actuales
SELECT 
    TABLE_NAME AS 'Tabla',
    ENGINE AS 'Motor Actual',
    TABLE_ROWS AS 'Filas',
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Tamaño (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'maintenance_db'
ORDER BY TABLE_NAME;

-- 4. Convertir todas las tablas a InnoDB
-- IMPORTANTE: Hacer backup antes de ejecutar estas conversiones

-- Tablas de Django
ALTER TABLE django_migrations ENGINE=InnoDB;
ALTER TABLE django_content_type ENGINE=InnoDB;
ALTER TABLE django_session ENGINE=InnoDB;
ALTER TABLE django_admin_log ENGINE=InnoDB;

-- Tablas de autenticación
ALTER TABLE auth_group ENGINE=InnoDB;
ALTER TABLE auth_group_permissions ENGINE=InnoDB;
ALTER TABLE auth_permission ENGINE=InnoDB;
ALTER TABLE auth_user ENGINE=InnoDB;
ALTER TABLE auth_user_groups ENGINE=InnoDB;
ALTER TABLE auth_user_user_permissions ENGINE=InnoDB;

-- Tablas de JWT
ALTER TABLE token_blacklist_blacklistedtoken ENGINE=InnoDB;
ALTER TABLE token_blacklist_outstandingtoken ENGINE=InnoDB;

-- Tablas de la aplicación
ALTER TABLE api_equipment ENGINE=InnoDB;
ALTER TABLE api_maintenance ENGINE=InnoDB;
ALTER TABLE api_photo ENGINE=InnoDB;
ALTER TABLE api_signature ENGINE=InnoDB;
ALTER TABLE api_secondsignature ENGINE=InnoDB;
ALTER TABLE api_report ENGINE=InnoDB;
ALTER TABLE api_auditlog ENGINE=InnoDB;

-- 5. Verificar que todas las tablas usen InnoDB
SELECT 
    TABLE_NAME AS 'Tabla',
    ENGINE AS 'Motor',
    CASE 
        WHEN ENGINE = 'InnoDB' THEN '✓ OK'
        ELSE '✗ Necesita conversión'
    END AS 'Estado'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'maintenance_db'
ORDER BY ENGINE, TABLE_NAME;

-- 6. Verificar integridad de las tablas después de la conversión
CHECK TABLE api_equipment;
CHECK TABLE api_maintenance;
CHECK TABLE api_photo;
CHECK TABLE api_signature;
CHECK TABLE api_secondsignature;
CHECK TABLE api_report;
CHECK TABLE api_auditlog;

-- 7. Optimizar tablas después de la conversión
OPTIMIZE TABLE api_equipment;
OPTIMIZE TABLE api_maintenance;
OPTIMIZE TABLE api_photo;
OPTIMIZE TABLE api_signature;
OPTIMIZE TABLE api_secondsignature;
OPTIMIZE TABLE api_report;
OPTIMIZE TABLE api_auditlog;
