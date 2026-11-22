import random
import time


def is_guess_correct(guess, sequence):
    '''Team-written: Receives the user's guess as a list, and the correct list sequence
    Loops through the user's guess and verifies if it matches the correct sequence
    Returns the answer status as a boolean'''
    answer_count = 0
    answer_status = False
    for j in range(len(guess)):
        if guess[j] == sequence[j]:
            answer_count += 1
        if answer_count == len(guess):
            answer_status = True
    
    return answer_status

def randomizer(options, length):
    '''Team-written: Receives a list of possible options and a length
    Generates a random list of the possible options of the given length
    Returns the random list'''
    random_list = []
    for i in range(length):
        random_list.append(random.choice(options))
    return random_list

def yell_leaders(attempt):
    '''Team-written: Receives the user's current attempt
    Checks the user's guess against a randomly genereated correct sequence of yells
    If the user enters the correct sequence every time, up to the list length, the function returns the win_status as True
    If the user enters any incorrect guesses, the function returns the win status as False'''
    choices = ["Gig 'em Aggies", "Farmer's Fight", "BTHO", "Ol' Army Fight"]
    sequence = randomizer(choices, 4)
    sequence_complete = False
    win_status = False
    i = 0
    # First clue is outside the loop because they need something to guess from to start
    print(sequence[i])
    while sequence_complete == False:
        time.sleep(1)
        for i in range(20):
            print(" ") # These blank prints are to cover the previous answer, feel free to change if something visual works better
        user_guess = input(f"Enter your guess: ")
        user_sequence = user_guess.split(", ")
        
        # Checks if the most recent guess sequence was correct
        answer_status = is_guess_correct(user_sequence, sequence)
        if answer_status == True:
            # Checks if the user has guessed correctly 4 times
            if len(user_sequence) == len(sequence):
                sequence_complete = True
                win_status = True
                return win_status
            print(f"Correct!")
            i += 1
            # Prints next clue
            for l in range(1,len(user_sequence)+1):
                for i in range(20):
                    print(" ")
                print(f"{sequence[:l+1]}")
            time.sleep(1)
            for i in range(20):
                print(" ")

        elif answer_status == False:
            print(f"Incorrect! That was attempt number {attempt}.")
            win_status = False
            return win_status

            
def yell_leaders_play_loop():
    '''Team-written: Keeps track of how many attempts the user has taken at the mini-game
    Prints instructions for how the game is played
    If the user wins the mini-game, the function returns the clue letter string "A" '''
    print(f'Welcome to a mini-game called "Follow the Yell Leaders"!')
    time.sleep(1)
    print(f"Here are the rules:")
    print(f'- The goal is to remember each new yell in sequence, similar to the toy "Simon".')
    print(f"- As each new yell is added, you need to remember all the ones that came before it.")
    print(f"- For formatting, enter each guess after the first as a comma-separated list, and\n  write your answer with the same capitalization as the clue.")
    print(f"- The sequence will go to 4 yells, and you have 3 attempts to complete this mini-game.")
    time.sleep(1)
    ready = input(f"When you're ready, click enter. ")
    if ready == "":
        time.sleep(0.5)
        print(f"-----------------------------------------")
        print(f"  ")
        time.sleep(0.5)

        attempt = 1
        status = yell_leaders(attempt)

        # Keeps track of attempts, kicks out the user if they failed 3 times
        while attempt < 3:
            if status == True:
                time.sleep(0.5)
                print(f"  ")
                print(f"-----------------------------------------")
                print(f"  ")
                print('Congratulations, you win! The letter you receive is "A".')
                return "A"
                break
            elif status == False:
                attempt += 1
                time.sleep(0.5)
                print(f"-----------------------------------------")
                print(f"  ")
                status = yell_leaders(attempt)

        if attempt == 3:
            print(f"Unfortunately you have run out of attempts for this mini-game!")
            # Let me know if this should return something for the game's fail condition

# I put the whole game loop into a function so it can be easier to call in the main game loop
letter = yell_leaders_play_loop()





