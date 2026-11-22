import random

def directions():
    """Team-written: Create a list of correct directions for the maze"""
    options = ["L", "R"]
    key = random.choices(options, k=4)
    return key


def maze(key):
    """Team-written: Take set of correct directions, and have the player make guesses of left/right. Check if guesses match, and make user restart their
    series of guesses after each incorrect guess."""
    
    
    win = False
    while (win == False):
        correct_guesses = []    
        
        
        for i in key:
            direction_guess = ''
            while direction_guess != "L" and direction_guess != "R":
                        direction_guess = input('Guess a direction: "L" or "R":').upper()
                        if direction_guess != "L" and direction_guess != "R":
                            print("Please type L or R, try again.")
                        else:
                            break
            if direction_guess == i:
                correct_guesses.append(direction_guess)
                print(f"Correct! {correct_guesses}")
                if len(correct_guesses)==4:
                    win = True
            if direction_guess != i:
                print(f"Sorry, wrong way! Start over.")
                break
                
            
    print("Frodo has made it to Professor Spears' office!")
def main():
    key = directions()

    maze(key)
    
main()
print("Yay! Frodo gets a new letter, Q.")
