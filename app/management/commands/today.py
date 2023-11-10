# type: ignore

from pprint import pprint

from django.core.management import BaseCommand

from app.service.today_page import get_today_page


class Command(BaseCommand):
    help = "Call get_today_page function"

    def handle(self, *args, **options):
        page = get_today_page(1)
        pprint(page)
