import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """
    Команда 'load_ingredients' загружает ингредиенты
    в базу из csv файла, который располагается в
    директории /data/.
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--ingredients',
            type=str,
            nargs='?',
            help='Загрузка данных в базу данных из файла ingredients.csv'
        )

    def handle(self, *args, **options):
        with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                  encoding='utf-8') as f:
            data = csv.reader(f)
            for row in data:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
