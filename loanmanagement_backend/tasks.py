from loans.models import User
from loans.constants import MIN_CREDIT_SCORE, MAX_CREDIT_SCORE, HIGH_BALANCE, LOW_INCOME
from loans.models import User, Transaction
from celery import shared_task
from decimal import Decimal


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

    transactions = Transaction.objects.filter(user=user.id)

    total_balances = Decimal('0')

    for transaction in transactions:
        if transaction.transaction_type == 'CREDIT':
            total_balances += transaction.amount
        elif transaction.transaction_type == 'DEBIT':
            total_balances -= transaction.amount

    total_balance = Decimal(total_balances)

    if total_balance >= high_balance:
        credit_score = max_credit_score
    elif total_balance > low_income:
        balance_difference = total_balance - low_income
        credit_score -= (balance_difference // 15000) * 10

    credit_score = max(min_credit_score, min(max_credit_score, credit_score))

    user.credit_score = credit_score
    user.save()

    return credit_score
