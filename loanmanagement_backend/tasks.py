from loans.models import User
from loans.constants import MIN_CREDIT_SCORE, MAX_CREDIT_SCORE, HIGH_BALANCE, LOW_INCOME, TRANSACTIONS_FILE
from loans.models import User
from celery import shared_task
from decimal import Decimal
import csv


@shared_task(bind=True)
def calculate_credit_score(self, annual_income, user_id):
    min_credit_score = MIN_CREDIT_SCORE
    max_credit_score = MAX_CREDIT_SCORE

    low_income = LOW_INCOME
    high_balance = HIGH_BALANCE
    total_balance = 0

    user = User.objects.get(id=user_id)

    if annual_income >= low_income:
        credit_score = max_credit_score
    else:
        credit_score = min_credit_score

    with open(TRANSACTIONS_FILE, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            transaction_type = row['transaction_type']
            amount = Decimal(row['amount'])

            if transaction_type == 'CREDIT':
                total_balance += amount
            elif transaction_type == 'DEBIT':
                total_balance -= amount

    total_balances = Decimal('0')

    # this i have used for management command leave it you can use directly from csv file

    # transactions = Transaction.objects.filter(user=user.id)
    # for transaction in transactions:
    #     if transaction.transaction_type == 'CREDIT':
    #         total_balances += transaction.amount
    #     elif transaction.transaction_type == 'DEBIT':
    #         total_balances -= transaction.amount

    total_balances = Decimal(total_balance)

    if total_balances >= high_balance:
        credit_score = max_credit_score
    elif total_balances <= low_income:
        credit_score = min_credit_score
    else:
        balance_difference = total_balances - low_income
        credit_score_change = int(balance_difference / Decimal('15000')) * 10

        credit_score = max(min_credit_score, min(max_credit_score, max_credit_score - credit_score_change))

    user.credit_score = credit_score
    user.save()

    return credit_score
