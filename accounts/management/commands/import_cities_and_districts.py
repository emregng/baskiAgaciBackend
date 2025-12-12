import json
from django.core.management.base import BaseCommand
from accounts.models import City, District

class Command(BaseCommand):
    help = 'Import cities and districts from JSON files'

    def handle(self, *args, **options):
        with open('sehirler.json', encoding='utf-8') as f:
            cities = json.load(f)
            for city in cities:
                City.objects.update_or_create(
                    code=int(city['sehir_id']),
                    defaults={'name': city['sehir_adi'].upper()}
                )
        self.stdout.write(self.style.SUCCESS('Cities imported.'))

        with open('ilceler.json', encoding='utf-8') as f:
            districts = json.load(f)
            for district in districts:
                city = City.objects.get(code=int(district['sehir_id']))
                District.objects.update_or_create(
                    id=int(district['ilce_id']),
                    defaults={
                        'name': district['ilce_adi'].upper(),
                        'city': city
                    }
                )
        self.stdout.write(self.style.SUCCESS('Districts imported.'))