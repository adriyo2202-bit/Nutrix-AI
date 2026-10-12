import sys
from diet_planner.planner import generate_engaging_diet_plan

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{GREEN}  {title.upper()}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")

def get_validated_input(prompt, cast_type, error_msg):
    while True:
        try:
            val = input(f"{BOLD}{WHITE}{prompt}{RESET} ").strip()
            return cast_type(val)
        except ValueError:
            print(f"{YELLOW}Invalid input. {error_msg}{RESET}")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Exiting...{RESET}")
            sys.exit(0)

def main():
    print_header("Engaging AI Diet Planner (Ollama Powered)")
    
    age = get_validated_input("Enter your age:", int, "Please enter a valid whole number for age.")
    height = get_validated_input("Enter your height in cm:", float, "Please enter a valid number for height.")
    weight = get_validated_input("Enter your weight in kg:", float, "Please enter a valid number for weight.")
    
    print(f"\n{BOLD}{WHITE}What is your primary goal?{RESET}")
    print("1. Body building")
    print("2. Just be fit")
    
    goal_str = "Just be fit"
    while True:
        try:
            goal_choice = input(f"{BOLD}{WHITE}Choose 1 or 2: {RESET}").strip()
            if goal_choice == '1':
                goal_str = "Body building"
                break
            elif goal_choice == '2':
                goal_str = "Just be fit"
                break
            else:
                print(f"{YELLOW}Invalid choice. Enter 1 or 2.{RESET}")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Exiting...{RESET}")
            sys.exit(0)

    print(f"\n{CYAN}🤖 Sending your details to the AI Coach... Please wait!{RESET}\n")
    
    # Call the Ollama API
    result = generate_engaging_diet_plan(age, height, weight, goal_str)
    
    print_header("Your Personalized AI Coach Output")
    print(result)
    print(f"\n{BOLD}{GREEN}Stay healthy! Goodbye.{RESET}\n")

if __name__ == "__main__":
    main()
