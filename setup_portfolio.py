import json
import os

def get_float_input(prompt, default=None):
    while True:
        user_input = input(prompt)
        if not user_input and default is not None:
            return default
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def main():
    print("--- Portfolio Setup ---")
    print("Please enter the following details to create your portfolio.json file.\n")

    shares_tqqq = get_float_input("Enter number of TQQQ shares: ")
    buy_price_tqqq = get_float_input("Enter average buy price for TQQQ: ")
    
    shares_agg = get_float_input("Enter number of AGG shares: ")
    buy_price_agg = get_float_input("Enter average buy price for AGG: ")
    
    q_baseline = input(f"Enter quarter baseline price for TQQQ [Default: {buy_price_tqqq}]: ")
    if not q_baseline:
        q_baseline = buy_price_tqqq
    else:
        try:
            q_baseline = float(q_baseline)
        except ValueError:
            print(f"Using default: {buy_price_tqqq}")
            q_baseline = buy_price_tqqq

    portfolio_data = {
        "shares_tqqq": shares_tqqq,
        "buy_price_tqqq": buy_price_tqqq,
        "shares_agg": shares_agg,
        "buy_price_agg": buy_price_agg,
        "quarter_baseline_price_tqqq": q_baseline
    }

    with open("portfolio.json", "w") as f:
        json.dump(portfolio_data, f, indent=4)

    print(f"\n✅ Success! 'portfolio.json' has been created.")

if __name__ == "__main__":
    main()
