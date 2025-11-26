# ADR-002: Elección de Librería para Generación de PDFs

## Estado
Aceptado

## Contexto
Necesitamos generar reportes en PDF para mantenimientos de equipos. Los reportes incluirán datos de equipos, mantenimientos, fotos y firmas. Debemos elegir entre WeasyPrint y ReportLab.

## Decisión
Implementaremos WeasyPrint para la generación de PDFs basada en HTML/CSS.

## Razón
- **Facilidad de uso**: Permite usar templates HTML con CSS para diseñar reportes, más intuitivo que código Python puro.
- **Flexibilidad**: Soporte completo para CSS, incluyendo layouts complejos, imágenes y estilos.
- **Integración**: Fácil integración con Django templates.
- **Mantenimiento**: Menos código personalizado, más mantenible.
- **Calidad**: Mejor renderizado de texto, imágenes y layouts.

## Consecuencias
- Dependencia de librerías del sistema (Pango, Cairo) para renderizado.
- Archivos PDF generados desde HTML templates.
- Posible sobrecarga en servidor para reportes complejos.

## Alternativas Consideradas
- ReportLab: Generación programática de PDFs. Más control fino pero más complejo para layouts.

## Resultados del Spike
- WeasyPrint: Implementado en 1h, genera PDFs de calidad con templates HTML.
- ReportLab: Requiere más código para layouts similares.
