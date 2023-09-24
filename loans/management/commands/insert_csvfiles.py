#optional 

# import csv
# from django.core.management.base import BaseCommand
# from ...models import Transaction

# class Command(BaseCommand):

#     help = 'Inserting transactions from a CSV file'

#     def add_arguments(self, parser):
#         parser.add_argument('csv_file', type=str, help='/Users/satyanarendrareddybudati/Desktop/projects/loanmanagement_backend/transactions_data Backend.csv')

#     def handle(self, *args, **kwargs):
#         csv_file = kwargs['csv_file']
        
#         try:
#             with open(csv_file, 'r') as file:
#                 reader = csv.DictReader(file)
#                 for row in reader:
                    
#                     row['user'] = 1

#                     Transaction.objects.create(
#                         user_id=row['user'],
#                         date=row['date'],
#                         transaction_type=row['transaction_type'],
#                         amount=row['amount']
#                     )

#             self.stdout.write(self.style.SUCCESS('Successfully inserted transactions from a CSV file'))
        
#         except FileNotFoundError:
#             self.stderr.write(self.style.ERROR('CSV file not found'))
