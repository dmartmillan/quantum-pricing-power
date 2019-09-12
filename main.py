import argparse
import sys

parser = argparse.ArgumentParser(prog='Program')

def main():
    args = parser.parse_args()
    print("Hello quantum!")
    val = input("Enter your value: ") 
    while (val != str("call") and val != str("put")):
        val = input("Oops! The value was wrong. Try again...\nEnter your value: ") 
    else: print(val)

if __name__== "__main__":
    main()
