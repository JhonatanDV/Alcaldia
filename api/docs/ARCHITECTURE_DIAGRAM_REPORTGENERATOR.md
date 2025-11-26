# Arquitectura del Patrón ReportGenerator

## Diagrama de Clases

```
ReportGenerator (Service Class)
├── __init__(self, template_name: str)
├── generate_report(self, context: dict) -> bytes
│   ├── render_template(context) -> str
│   ├── convert_html_to_pdf(html_content) -> bytes
│   └── return pdf_bytes
└── validate_data(self, context: dict) -> bool

ReportViewSet (DRF ViewSet)
├── create(self, request) -> Response
│   ├── validate_request_data()
│   ├── fetch_equipment_data()
│   ├── generate_report()
│   ├── save_to_storage()
│   └── return_presigned_url()
└── get_queryset() -> QuerySet

Report (Model)
├── id: AutoField (PK)
├── equipment: ForeignKey(Equipment)
├── generated_by: ForeignKey(User)
├── report_data: JSONField
├── pdf_file: FileField
├── created_at: DateTimeField
└── expires_at: DateTimeField

Dependencies:
- WeasyPrint (for HTML to PDF)
- Django Templates (for report layout)
- MinIO/boto3 (for PDF storage)
- DRF (for API endpoints)
```

## Flujo de Generación de Reporte

1. Usuario solicita reporte via POST /api/reports/
2. ReportViewSet valida datos (equipment_id, date_range)
3. Fetch data: Equipment + Maintenances + Photos + Signatures
4. ReportGenerator.render_template() con context
5. ReportGenerator.convert_html_to_pdf()
6. Save PDF to MinIO, generate presigned URL
7. Create Report instance in DB
8. Return presigned URL to client

## Patrón de Diseño
- **Service Layer**: ReportGenerator encapsula lógica de generación
- **Repository**: Models para persistencia
- **Controller**: ViewSet maneja requests/responses
- **Storage Abstraction**: MinIO para archivos PDF
