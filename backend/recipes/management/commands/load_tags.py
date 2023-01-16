import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipe.models import Tags

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """
    Добавляем теги из файла CSV.
    После миграции БД запускаем командой
    python manage.py load_tags локально
    или
    sudo docker-compose exec backend python manage.py load_tags
    на удаленном сервере.
    Создает записи в модели Tag из списка.
    """
    help = 'Загрузка данных из csv файлов.'

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            default='tags.csv',
                            nargs='?',
                            type=str)

    def handle(self, *args, **kwargs):
        try:
            with open(os.path.join(DATA_ROOT, kwargs['filename']), 'r',
                      encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    Tags.objects.get_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
        except FileNotFoundError:
            raise CommandError('Файл tags нужно добавить в директорию data')
