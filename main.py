import argparse
import sys
from options import EuropeanCallOption

parser = argparse.ArgumentParser(prog='Program')

def main():
    args = parser.parse_args()
    print("Welcome to Quantum Pricing Power!\n")
    val = input("Enter your option (Call /Put):").lower()
    while (val  != str("call") and val != str("put")):
        val = input("Oops! The option was wrong. Try again...\nEnter your option (call / put): ").lower() 
    
    print('Option selected:', val, '\n')
    
    spot_price = input("Enter spot price:")
    while ( isinstance(spot_price, int)):
        spot_price = input("Oops! The spot price was wrong. Try again...\nEnter spot price: ")
    
    volatility = input("Enter volatility:")
    while ( isinstance(volatility, float)):
        volatility = input("Oops! The volatility was wrong. Try again...\nEnter volatility: ")
    
    int_rate = input("Enter interest rate:")
    while ( isinstance(int_rate, float)):
        int_rate = input("Oops! The interest rate was wrong. Try again...\nEnter interest rate: ")
    
    days = input("Enter days to maturity:")
    while ( isinstance(days, int)):
        days = input("Oops! Days to maturity was wrong. Try again...\nEnter days to maturity: ")
        
    strike_price = input("Enter strike price:")
    while ( isinstance(strike_price, float)):
        strike_price = input("Oops! The strike price was wrong. Try again...\nEnter strike price: ")
        
    print('Initialize algorithm...\n')
    european_option = EuropeanCallOption(val,spot_price, volatility, int_rate, days,strike_price)
    print('Plotting probability distribution... \n')
    european_option.plot_probability_distribution()
    print('Plotting payoff function... \n')
    european_option.plot_payoff_function()
    
    european_option.print_exact_values()
    print('Evaluating expected payoff... \n')
    european_option.evaluate_expected_payoff()
    print('Plotting estimated data values... \n')
    european_option.plot_estimated_data_values()
    print('Evaluating delta values... \n')
    european_option.evaluate_delta()
    print('Plotting delta values... \n')
    european_option.plot_estimated_delta_values()

if __name__== "__main__":
    main()
