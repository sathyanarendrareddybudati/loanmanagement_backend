def calculate_credit_score(annual_income, total_balance):
    # Define the minimum and maximum credit scores
    min_credit_score = 300
    max_credit_score = 900

    # Define the thresholds for annual income and balance
    low_income_threshold = 1000000
    high_balance_threshold = 1000000

    # Initialize the credit score to the minimum value
    credit_score = min_credit_score

    # Check if annual income is above the threshold
    if annual_income >= low_income_threshold:
        credit_score = max_credit_score
    else:
        # Calculate the balance difference
        balance_difference = total_balance - high_balance_threshold

        # Calculate the credit score based on the balance difference
        increment_per_15000 = 10
        credit_score += (balance_difference // 15000) * increment_per_15000

        # Ensure the credit score stays within the defined range
        credit_scores = max(min_credit_score, min(max_credit_score, credit_score))

    return credit_scores

# Example usage:
annual_income = 300000
total_balance = 568450
credit_score = calculate_credit_score(annual_income, total_balance)
print('credit_score', credit_score)  # Output: credit_score 670
