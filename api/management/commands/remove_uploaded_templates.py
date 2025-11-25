from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from api.models import Template


class Command(BaseCommand):
    help = 'Elimina todos los registros de plantillas (Template) y borra los archivos asociados en storage.'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Confirmar eliminación sin preguntar.')

    def handle(self, *args, **options):
        confirm = options.get('yes', False)

        qs = Template.objects.all()
        total = qs.count()
        if total == 0:
            self.stdout.write('No hay registros de Template para eliminar.')
            return

        self.stdout.write(f'Se encontraron {total} registros de Template.')
        if not confirm:
            confirm_input = input('Va a eliminar todas las plantillas y sus archivos asociados. Continuar? [y/N]: ')
            if confirm_input.strip().lower() not in ('y', 'yes'):
                self.stdout.write('Operación cancelada por el usuario.')
                return

        deleted = 0
        errors = 0
        for t in qs:
            try:
                # Attempt to delete associated file if present
                try:
                    if t.template_file and t.template_file.name:
                        if default_storage.exists(t.template_file.name):
                            default_storage.delete(t.template_file.name)
                except Exception as e:
                    self.stderr.write(f'Advertencia: no se pudo borrar archivo de Template id={t.id}: {e}')

                t.delete()
                deleted += 1
                self.stdout.write(f'Eliminada Template id={t.id} name="{t.name}"')
            except Exception as e:
                errors += 1
                self.stderr.write(f'Error eliminando Template id={getattr(t, "id", "?")}: {e}')

        self.stdout.write(f'Resumen: eliminadas={deleted}, errores={errors}')
