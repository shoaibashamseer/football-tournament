import csv
from django.core.management.base import BaseCommand
from ticketapp.models import SeatAllocation

class Command(BaseCommand):
    help = 'Upload seat data from a CSV file to SeatAllocation table'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                SeatAllocation.objects.create(
                    seat_number=row['No'],
                    qr_code_data=row['Code']
                )
        self.stdout.write(self.style.SUCCESS('Data uploaded successfully!'))
