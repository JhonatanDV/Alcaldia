from api.models import Template
templates = Template.objects.all()
print(f'Total templates: {templates.count()}')
for t in templates:
    print(f'id={t.id}, name={t.name}, file={getattr(t.template_file, "name", None)}')