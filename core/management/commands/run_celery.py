import subprocess
import sys
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Запуск Celery worker'

    def handle(self, *args, **options):
        self.stdout.write(' Запуск Celery worker со встроенным брокером...')
        subprocess.Popen(['celery', '-A', 'config', 'worker', '--loglevel=info'])
        self.stdout.write(' Celery worker запущен')
