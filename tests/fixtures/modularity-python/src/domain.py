from decimal import Decimal


def positive_amount(value):
    amount = Decimal(value)
    if amount <= 0:
        raise ValueError('amount must be positive')
    return amount
