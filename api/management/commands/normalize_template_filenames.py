from django.core.management.base import BaseCommand
from django.core.files import File as DjangoFile
from django.core.files.storage import default_storage
from api.models import Template
import os


class Command(BaseCommand):
    help = 'Normaliza nombres de archivos en Template.template_file y mueve/renombra en storage. Por defecto hace dry-run; use --commit para aplicar.'

    def add_arguments(self, parser):
        parser.add_argument('--commit', action='store_true', help='Aplicar cambios (mover/renombrar archivos). Si no se indica, sólo muestra plan).')

    def handle(self, *args, **options):
        commit = options.get('commit', False)

        qs = Template.objects.exclude(template_file__isnull=True).exclude(template_file__exact='')
        if not qs.exists():
            self.stdout.write('No hay plantillas con archivo para procesar.')
            return

        for t in qs:
            current_name = t.template_file.name  # e.g. 'templates/Formato_...pdf'
            if not current_name:
                continue
            basename = os.path.basename(current_name)
            try:
                normalized = Template._normalize_filename(basename)
            except Exception:
                normalized = basename

            if normalized == basename:
                self.stdout.write(f'OK (sin cambios) Template id={t.id}: {current_name}')
                continue

            planned_target = os.path.join('templates', normalized)

            # avoid collisions: if target exists, append numeric suffix
            final_target = planned_target
            if default_storage.exists(final_target):
                base, ext = os.path.splitext(normalized)
                i = 1
                while default_storage.exists(os.path.join('templates', f"{base}_{i}{ext}")):
                    i += 1
                final_target = os.path.join('templates', f"{base}_{i}{ext}")

            self.stdout.write(f"Plan: Template id={t.id} -> {current_name}  =>  {final_target}")

            if not commit:
                continue

            # Commit: copy to new name and delete old
            try:
                with default_storage.open(current_name, 'rb') as src:
                    django_file = DjangoFile(src)
                    saved_name = default_storage.save(final_target, django_file)

                # Attempt to delete original (best-effort)
                try:
                    default_storage.delete(current_name)
                except Exception as e:
                    self.stderr.write(f'Advertencia: no se pudo eliminar {current_name}: {e}')

                # Update model reference
                t.template_file.name = saved_name
                t.save(update_fields=['template_file'])
                self.stdout.write(f'Hecho: Template id={t.id} renombrado a {saved_name}')
            except Exception as e:
                self.stderr.write(f'Error procesando {current_name} (Template id={t.id}): {e}')
