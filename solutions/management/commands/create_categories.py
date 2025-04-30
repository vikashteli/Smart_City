from django.core.management.base import BaseCommand
from solutions.models import Category

class Command(BaseCommand):
    help = 'Creates initial categories for the SmartCity Solutions Hub'

    def handle(self, *args, **kwargs):
        categories = [
            'Transportation',
            'Environment',
            'Energy',
            'Infrastructure',
            'Public Services',
            'Technology',
            'Community',
            'Safety',
            'Healthcare',
            'Education'
        ]

        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created category "{category_name}"'))
