# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None      # set if the user wins or ends the game
guess_displayed = 0     # binary output on LEDs
key = 0                 # Guess objective
Buzzer = None           # Buzzer output
AccuracyLED = None      # Accuracy LED output
score = 0               # Player's guess score
name = ""               # Player's name
count = 0               # Number of highscores
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print(" _   _                 _                  _____ _            __  __ _        ")
    print("| \ | |               | |                / ____| |          / _|/ _| |       ")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___   ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\ ")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/  ")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|  ")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, key
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        key = value
        #print(key)
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")



def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    raw_data.sort(key=lambda x: x[1])
    for i in range(3):
        print(str(i+1)+" - " + raw_data[i][0]+ " took "+str(raw_data[i][1])+" guesses\r")
    pass



# Setup Pins
def setup():
    global AccuracyLED, Buzzer, score
    score = 0

    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    # Setup regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)  #LED
    GPIO.setup(LED_value[1], GPIO.OUT)  #LED
    GPIO.setup(LED_value[2], GPIO.OUT)  #LED
    GPIO.setup(32, GPIO.OUT)            #PWM LED
    GPIO.setup(33, GPIO.OUT)            #PWM BUZZER

    # Setup PWM channels
    if AccuracyLED is None:
        AccuracyLED = GPIO.PWM(32, 1000)
    if Buzzer is None:
        Buzzer = GPIO.PWM(33, 1000)  
    AccuracyLED.start(0)

    # Setup debouncing and callbacks
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING,   callback=btn_increase_pressed,    bouncetime=200)
    GPIO.add_event_detect(btn_submit,   GPIO.FALLING,   callback=btn_guess_pressed,       bouncetime=200)
    pass



# Load high scores
def fetch_scores():
    # get however many scores there are
    num_of_highscores = eeprom.read_byte(0)
    scores = eeprom.read_block(1,4*num_of_highscores)
    # Get the scores
    global name, score
    # convert the codes back to ascii
    for i in range(len(scores)):
        if (i+1)%4 != 0:
            scores[i] = chr(scores[i])
    
    Names_and_scores = []
    for I in range(0, num_of_highscores*4-1, 4):
        Names_and_scores.append([scores[I-4]+scores[I-3]+scores[I-2],scores[I-1]])    
    # return back the results
    return num_of_highscores, Names_and_scores



# Save high scores
def save_scores():
    global score, name
    # fetch scores
    count, scores = fetch_scores()
    # include new score
    count += 1
    eeprom.write_byte(0, count)
    scores.append([name,score])
    print(scores)
    scores.sort(key=lambda x: x[1])
    for i, score in enumerate(scores):
        data_to_write = []
        # get the string
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
        eeprom.write_block(i+1, data_to_write)
    pass



# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)



# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    is_pressed = GPIO.input(btn_increase)
    global guess_displayed
    if  is_pressed == 0:
        guess_displayed += 1
        if guess_displayed == 8:
            guess_displayed = 0
    if guess_displayed==0:
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif guess_displayed==1:
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif guess_displayed==2:
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif guess_displayed==3:
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.LOW)
    elif guess_displayed==4:
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif guess_displayed==5:
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.LOW)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif guess_displayed==6:
        GPIO.output(LED_value[0],GPIO.LOW)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.HIGH)
    elif guess_displayed==7:
        GPIO.output(LED_value[0],GPIO.HIGH)
        GPIO.output(LED_value[1],GPIO.HIGH)
        GPIO.output(LED_value[2],GPIO.HIGH)
    pass



# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    global guess_displayed, key, score, name, AccuracyLED, Buzzer
    LED_DutyCycle = 0
    is_pressed = GPIO.input(btn_submit)
    if is_pressed == 0:
        start_time = time.time()
        while GPIO.input(btn_submit) == GPIO.LOW:
            pass
        if time.time()-start_time>=1:
            GPIO.remove_event_detect(btn_increase)
            GPIO.remove_event_detect(btn_submit)
            GPIO.output(LED_value[0],GPIO.LOW)
            GPIO.output(LED_value[1],GPIO.LOW)
            GPIO.output(LED_value[2],GPIO.LOW)
            GPIO.cleanup()
            setup()
            welcome()
            menu()

        score += 1
        diff=abs(guess_displayed-key)
        if guess_displayed < key:
            LED_DutyCycle = 100*guess_displayed/key
        else:
            LED_DutyCycle = 100*diff/8
        # Change the PWM LED
        accuracy_leds(LED_DutyCycle)
        # if it's close enough, adjust the buzzer
        trigger_buzzer(diff)
        # if it's an exact guess:
        # - Disable LEDs and Buzzer
        if guess_displayed == key:
            AccuracyLED.stop(0)
            Buzzer.stop(0)
            GPIO.remove_event_detect(btn_increase)
            GPIO.remove_event_detect(btn_submit)
            GPIO.output(LED_value[0],GPIO.LOW)
            GPIO.output(LED_value[1],GPIO.LOW)
            GPIO.output(LED_value[2],GPIO.LOW)
            # - tell the user and prompt them for a name
            name = input("You guessed the correct number in " + str(score) + " guesses!\nPlease enter your name (3 characters only): ")
            save_scores()
            GPIO.cleanup()
            setup()
            welcome()
            menu()
    pass


# LED Brightness
def accuracy_leds(LED_DutyCycle):
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global AccuracyLED
    GPIO.output(32,GPIO.HIGH)
    AccuracyLED.ChangeDutyCycle(LED_DutyCycle)
    pass


# Sound Buzzer
def trigger_buzzer(diff):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    Buzzer.ChangeDutyCycle(50)
    freq=(2**(abs(3-diff)))
    Buzzer.ChangeFrequency(100)
    if diff<=3 and diff>0:
        for I in range(freq):
            GPIO.output(33,GPIO.HIGH)
            Buzzer.start(0)
            time.sleep(1/freq)
            Buzzer.stop(0)
    GPIO.output(33, GPIO.LOW)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()