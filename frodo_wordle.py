import random

def wordbank():
    '''Team-written: return a list of possible words that a wordle game will randomly use'''
    with open("wordle_words.txt") as file:
        word_bank = []
        for line in file:
            word_bank.append(line.strip().lstrip("\ufeff"))
        file.close()
        return word_bank

def exist(s):
    '''Team-written: check if the input s is an existing 5 letter english word, return a bool'''
    with open("words.txt") as file:
        existing = []
        for line in file:
            existing.append(line.strip().upper())
        file.close()
    if s in existing:
        #if the word is valid, check what letters is right
        return True
    else:
        return False
    

def correctLetter(correct, input):
    '''Team-written: check what letter is right, return a list of 0, 1, 2--0 is not exist, 1 is exist but wrong index, 2 is correct index'''
    result = [0, 0, 0, 0, 0]
    checked = {}
    occurrence = {}
    matched = {}

    for i in range(0, 5):
        try:
            checked[input[i]] += 1
        except KeyError:
            checked[input[i]] = 1

        try:
            occurrence[correct[i]] += 1
        except KeyError:
            occurrence[correct[i]] = 1

        if input[i] == correct[i]:
            result[i] = 2
            try:
                matched[input[i]] += 1
            except KeyError:
                matched[input[i]] = 1
        elif input[i] in correct:
            result[i] = 1
        else:
            result[i] = 0

    for letter in matched:
        occurrence[letter] -= matched[letter]

    for i in range(0, 5):
        if result[i] == 1:
            if occurrence[input[i]] > 0:
                occurrence[input[i]] -= 1
            else:
                result[i] = 0

    return result

def letter_used(input, result):
    '''Team-written: takes the input and the result from correctletter; add those result to the map'''
    letters = {}
    alphebets = ["Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M"]
    for l in alphebets: #initialize the alphebet map
        letters[l] = -1

    for i in range (0,5):
        letters[input[i]] = result[i]
    return letters

    
def play():
    '''Team-written: ask for input and verify its validity'''

    word = input("Type a five letters word: ")
    word = word.upper()
    while len(word) != 5 or not exist(word):
        if len(word) != 5:
            word = input("Invalid input--the word must be FIVE letters. Please try again: ")
            word = word.upper()
            continue
        if not exist(word): #if the word isnt a existing english word
            word = input("Invalid input--the word must be a valid english word. Please try again: ")
            word = word.upper()
            continue
        
    return word
    
def wordle():
    '''Team-written: keep track of 3 attempts in total, generate different correct word every attempt'''
    word_bank = wordbank()
    round = 0
    intro = "Welcome to Aggie Wordle! This tests if you are a qualified Aggie"
    rule = "Every round you will get a random 5-letter word that is TAMU related.\n" \
            "Every round, you get 6 tries to input a word. You must get it right on the 6th try.\n" \
            "If you get the word right within 3 rounds, you will get the missing word piece for your anagram!\n" \
            "Good Luck! "
    print(intro)
    print(rule)

    while round < 3:
        word_this_round = random.choice(word_bank)
        word_bank.remove(word_this_round)
        print(f"Round {round+1}")
        round += 1
        attempt = 0
        #print(word_this_round) #need to delete when actually playing; only for testing
        while attempt < 6:
            print(f"Attempt {attempt+1}")
            valid_guess = play()
            corrects = correctLetter(word_this_round, valid_guess)
            print(corrects)

            #print the letter tracker
            letter_tracker  = letter_used(valid_guess, corrects)
            for key, value in letter_tracker.items():
                if key == "A" or key == "Z":
                    print("\n")
                print(f"{key} :{value}")
        
            #print(f"{letter_tracker[:11]} \n {letter_tracker[11:20]} \n {letter_tracker[20:27]}")
            if corrects == [2,2,2,2,2]:
                print("Congrulation! You found the word!")
                break
            attempt += 1
            if attempt == 6 and round != 3:
                print(f"Uh oh...You FAILED! That's okay, you still have {3-round} rounds left. \nFYI, you will get a new word next round")
            elif attempt == 6 and round == 3:
                print(f"You failed this game! You are not a qualified aggie. \nTherefore you won't get your word piece!")
        if corrects == [2,2,2,2,2]:
            print("You got a word piece......it's...... \"D\"!!")
            break


wordle()



