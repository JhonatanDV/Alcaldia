# ADR-001: Estrategia de Carga para Fotos de Mantenimiento

## Estado
Aceptado

## Contexto
La API de mantenimiento de equipos necesita manejar cargas de fotos para registros de mantenimiento. Necesitamos decidir entre cargas del lado del servidor (manejadas por Django) y cargas del lado del cliente usando URLs prefirmadas (ej. para S3/MinIO).

## Decision
Implementaremos cargas del lado del servidor usando el sistema de almacenamiento de archivos de Django, con MinIO como backend de almacenamiento para desarrollo y produccion.

## Razonamiento
- **Simplicidad**: El manejo del lado del servidor es directo con DRF y FileField/ImageField de Django.
- **Seguridad**: Mas facil hacer cumplir autenticacion y validacion en el servidor.
- **Costo**: No hay necesidad de logica de generacion de URLs prefirmadas.
- **Integracion**: MinIO es compatible con S3, permitiendo migracion facil a AWS S3 despues.
- **Pruebas**: Mas facil simular en pipelines CI/CD.

## Consecuencias
- El servidor manejara cargas de archivos, potencialmente aumentando la carga.
- Necesidad de configurar MinIO en configuraciones y CI.
- Archivos almacenados en MinIO, accesibles via endpoints de API.

## Alternativas Consideradas
- URLs prefirmadas: Mas complejas, requieren logica del lado del cliente, pero descargan trafico de carga.

## Resultados del Spike
- Lado del servidor: Implementado en 2h, funciona con serializadores DRF.
- Prefirmadas: Requeriria bibliotecas adicionales y cambios del cliente.
