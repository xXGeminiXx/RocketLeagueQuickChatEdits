import time
import pyautogui
import pygame
from random import sample

# Track recent messages and their timestamps
recent_messages = []

# Create your own word variations and format them like this (see examples on how to use them in the "edit" section below)
variations = {
    'Challenge': [
        'I dare you to score',
        'Try to beat that!',
        'Challenge accepted'
    ],
    'Confidence Boost': [
        'We\'re the Rocket League champions!',
        'Our teamwork is unbeatable!',
        'We\'re the best on the field!',
        'No one can match our Rocket League skills!',
        'Confidence in our plays leads to victory!',
        'We\'ve got this game in the bag!',
        'Trust in our abilities; we\'re unstoppable!',
        'Our Rocket League prowess knows no bounds!',
        'Believe in yourselves; we\'re the elite players!',
        'The field is our playground; let\'s dominate!',
        'Confidence breeds success; we\'re on fire!',
        'We\'re the Rocket League dream team!',
        'Our gameplay is top-notch; fear us!',
        'No one can outplay us in Rocket League!',
        'Confidence, teamwork, and victory – that\'s us!'
    ],
    'Encouraging Taunt': [
        'Is that all you\'ve got?',
        'Nice try, but not enough',
        'You\'re getting warmer! Keep pushing!',
        'Not bad, but can you top it?',
        'You\'re almost there! Don\'t stop now.',
        'Getting better with every try!',
        'You\'re on the right track; now, let\'s speed it up!',
        'Impressive, but I\'ve seen you do better!',
        'Keep trying, you\'re almost unbeatable!',
        'You\'re a force to be reckoned with!'
        'You can do better than that.'
    ],
    'Celebration': [
        'Great job, team!',
        'We\'re on fire!',
        'Calculated.',
        'WINNING!'
    ],
    'Apology': [
        'My bad, that was on me',
        'Sorry about that mistake',
        'Whoopsie... Sorry.'
    ],
    'affirmation': [
        '...maybe',
        '...possibly',
        '...sometimes',
        '...probably',
        '...definitely',
        '...no doubt',
        '...on every alternate Tuesday.',
        '...unless it’s a full moon.',
        '...only if the WiFi signal is strong.',
        '...assuming I\'ve had my coffee.',
        '...only in leap years.',
        '...give or take.',
        '...depending on the wind direction.',
        '...if planets align.',
        '...but don\'t quote me on that!',
        '...unless I forgot my socks',
        '...if it\'s not raining cats and dogs and whatnot.',
    ],
    'friend': [
        'ole Buddy.',
        'Pal.',
        'Mate.',
        'Champ.',
        'Comrade',
        'fellow gamer',
        'brother',
        'Bro!',
        'My Dude from another Latitude!',
        'My Partner in Digital-Crime!',
        'My Pixel Pal!',
        'home skillet',
        'Hey Chief!',
        'Mi Amigo!',
        'My Digital Sidekick!'
    ],
    'foe': [
        'Aggressive Rival.',
        'Mr. Challenger.',
        'Competitor.',
        'Primary Adversary.',
        'Nemesis.',
        'Antagonist.',
        'Digital Dance Partner.',
        'Keyboard Kombatant.',
        'Mysterious Stranger.',
        'Pixelated Enemy.',
        'you Digital Doppelganger.',
        'you Joystick Jouster.',
        'you Button Basher.',
        'Console Conqueror.'
    ],
    'compliment': [
        'Great!',
        'Awesome!',
        'Amazing!',
        'Fantastic!',
        'Impressive!',
        'Excellent!',
        'Outstanding!',
        'Stellar!',
        'Splendid!',
        'More Legendary than a Unicorn!',
        'Cooler than a Polar Bear’s Toenails!',
        'Shinier than a freshly waxed Penguin.',
        'As epic as a double rainbow!',
        'Worthy of a mic drop!',
        'As dazzling as fireworks!',
        'As radiant as the morning sun!',
        'As electrifying as a thunderstorm!',
        'A True Maestro!',
        'Nothing Short of Magic!'
    ],
    'cat fact': [
        'Cats have been domesticated for over 4,000 years.',
        'Cats sleep for an average of 12-16 hours a day.',
        'A group of cats is called a clowder.',
        'Cats have a specialized collarbone that allows them to always land on their feet.',
        'Cats have five toes on their front paws and four toes on their back paws.',
        'Cats have a third eyelid called a haw that helps protect their eyes.',
        'Cats have a specialized grooming claw on their front paws.',
        'Cats have a highly developed sense of hearing and can detect higher frequencies than humans.',
        'Cats have a keen sense of balance and are excellent climbers.',
        'Cats communicate with each other using a variety of vocalizations, body postures, and scents.',
        'Cats have a unique ability to rotate their ears 180 degrees.',
        'Cats have retractable claws that help them climb and maintain their hunting skills.',
        'Cats have a specialized tongue with tiny, backward-facing barbs called papillae.',
        'Cats have a Jacob\'s organ, also known as the vomeronasal organ, which allows them to analyze scent molecules.',
        'Cats have been associated with various mythologies and were worshipped in ancient civilizations.',
        'Cats have a flexible spine that enables them to twist and turn in mid-air while maintaining their balance.',
        'Cats have a strong instinct for cleanliness and spend a significant amount of time grooming themselves.',
        'Cats have a highly sensitive sense of touch, particularly in their whiskers and paws.',
        'Cats have a natural hunting instinct and may engage in playful stalking and pouncing behaviors.',
        'Cats have a remarkable ability to squeeze through small spaces due to their flexible bodies.',
        'Cats have a specialized nose pad that contains unique patterns, similar to human fingerprints.',
        'Cats have an average lifespan of 15-20 years, but some cats have lived well into their 30s.',
        'Cats have a complex vocal repertoire and can produce a variety of sounds, including meows, purrs, and chirps.',
        'Cats have a strong sense of territory and may mark their territory by rubbing against objects with their scent glands.',
        'Cats have an acute sense of night vision and can see in nearly total darkness.',
        'Cats have a preference for a clean litter box and may refuse to use a dirty one.',
        'Cats have a mysterious behavior known as the "slow blink," which is considered a sign of trust and affection.',
        'Cats have a natural curiosity and are known for exploring their surroundings with great interest.',
        'Cats have a specialized hunting technique called "whisker guidance" that helps them navigate narrow spaces.',
        'Cats have a unique ability to rotate their paws backward, allowing them to climb down trees headfirst.',
        'Cats have a highly adaptable diet and can thrive on a variety of food sources, including meat, fish, and even certain fruits and vegetables.',
        'Cats have been trying to text humans for years, but autocorrect keeps changing "meow" to "now."',
        'A cat’s dream job? Professional pillow tester.',
        'Cats believe they invented the internet. And honestly, they might be right.',
        'Cats secretly love cheesy pop songs. Don’t ask how we know.'
    ]
}

# DualSense controller button mappings for pygame
buttons = {
    'cross': 0,
    'circle': 1,
    'square': 2,
    'triangle': 3,
    'share': 4,
    'ps': 5,
    'options': 6,
    'L1': 9,
    'R1': 10,
    'up': 11,
    'down': 12,
    'left': 13,
    'right': 14,
}

# Time window given for button sequence macros (1.1 seconds).... you can change this as you please
macroTimeWindow = 1.1

# Time interval between spammed chats (0.2 seconds).... change as you please
chatSpamInterval = 0.2

# Edit these if necessary
chatKeys = {
    'lobby': 't',
    'team': 'y',
    'party': 'u'
}

firstButtonPressed = {
    'button': None,
    'time': 420
}

def resetFirstButtonPressed():
    global firstButtonPressed
    firstButtonPressed = {
        'button': None,
        'time': 420
    }

macrosOn = True

def combine(button1, button2):
    global numJoysticks
    for i in range(numJoysticks):
        if joysticks[i].get_button(buttons[button1]) and joysticks[i].get_button(buttons[button2]):
            resetFirstButtonPressed()
            return True
    return False

def sequence(button1, button2):
    global firstButtonPressed
    global numJoysticks
    functionCallTime = time.time()
    for i in range(numJoysticks):
        if firstButtonPressed['button'] == None:
            if joysticks[i].get_button(buttons[button1]):
                firstButtonPressed['time'] = functionCallTime
                firstButtonPressed['button'] = button1
                return False
        else:
            if functionCallTime > (firstButtonPressed['time'] + macroTimeWindow):
                if joysticks[i].get_button(buttons[button1]):
                    firstButtonPressed['time'] = functionCallTime
                    firstButtonPressed['button'] = button1
                    return False
                else:
                    resetFirstButtonPressed()
                    return False
            else:
                if joysticks[i].get_button(buttons[button2]):
                    if button1 == firstButtonPressed['button']:
                        if (functionCallTime > (firstButtonPressed['time'] + 0.05)):
                            resetFirstButtonPressed()
                            return True
                    else:
                        return False
    return False

def quickchat(thing, chatMode='lobby', spamCount=1):
    for i in range(spamCount):
        print(f"Sending quick chat: {thing} ({chatMode} mode)")
        pyautogui.press(chatKeys[chatMode])
        print("Pressing chat key")
        pyautogui.write(thing, interval=0.001)
        print("Writing quick chat")
        pyautogui.press('enter')
        print("Pressing enter")
        time.sleep(chatSpamInterval)

def toggleMacros(button):
    global numJoysticks
    for i in range(numJoysticks):
        if joysticks[i].get_button(buttons[button]):
            global macrosOn
            macrosOn = not macrosOn
            if macrosOn:
                print('----- quickchat macros toggled on -----\\n')
            else:
                print('----- quickchat macros toggled off -----\\n')
            time.sleep(0.2)

def shuffleVariations(key=''):
    if not (key == ''):
        lastWordUsed = shuffledVariations[key]['randomizedList'][len(variations[key]) - 1]
        secondLastWordUsed = shuffledVariations[key]['randomizedList'][len(variations[key]) - 2]
        while True:
            shuffledList = sample(variations[key], len(variations[key]))
            if not (shuffledList[0] == lastWordUsed) and (shuffledList[1] == secondLastWordUsed):
                shuffledVariations[key]['randomizedList'] = shuffledList
                shuffledVariations[key]['nextUsableIndex'] = 0
                break
    else:
        for key in variations:
            shuffledVariations[key] = {
                'randomizedList': sample(variations[key], len(variations[key])),
                'nextUsableIndex': 0
            }

def variation(key):
    global variations
    global shuffledVariations
    index = shuffledVariations[key]['nextUsableIndex']
    if not len(variations[key]) > 2:
        print(f'The "{key}" variation list has less than 3 items.....it cannot be used properly!! Please add more items (words/phrases)')
        return '-- "' + key + '" variation list needs more items --'
    else:
        if index < (len(variations[key])):
            randWord = shuffledVariations[key]['randomizedList'][index]
            shuffledVariations[key]['nextUsableIndex'] += 1
            return randWord
        else:
            shuffleVariations(key)
            randWord = shuffledVariations[key]['randomizedList'][0]
            shuffledVariations[key]['nextUsableIndex'] += 1
            return randWord

def is_recent_message(message, cooldown_seconds=600):  # 10 minutes cooldown by default
    current_time = time.time()
    for msg, timestamp in recent_messages:
        if msg == message and current_time - timestamp < cooldown_seconds:
            return True
    return False

def send_quick_chat(message):
    global lastQuickChat
    # If the message is the same as the last one, get another variation
    while message == lastQuickChat:
        message = variation(message.split()[-1]) # Assuming the variation key is the last word of the message
    # Track the last sent message
    lastQuickChat = message
    # Print the message
    print(f"Sent quick chat: {message}")
    quickchat(message, chatMode='lobby')



shuffledVariations = variations.copy()
shuffleVariations()
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
# Detect the controllers
detected_controllers = []

for controller in joysticks:
    if controller.get_init() == True:
        detected_controllers.append(controller)

if len(detected_controllers) > 0:
    for controller in detected_controllers:
        if "PS4" in controller.get_name():
            print("\n\n~~~~~~ PS4 Controller detected ~~~~~~\n\nwaiting for quickchat inputs....\n\n")
        elif "DualSense" in controller.get_name():
            print("\n\n~~~~~~ DualSense Wireless Controller detected ~~~~~~\n\nwaiting for quickchat inputs....\n\n")

lastQuickChat = ''
while True:
    try:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                numJoysticks = pygame.joystick.get_count()
                print("Button pressed:", event.button)
                toggleMacros('ps')
                if macrosOn:
                    if sequence('up', 'up'):
                        send_quick_chat("I got it" + variation('affirmation'))
                    elif sequence('up', 'down'):
                        send_quick_chat("Defending... but don't expect too much from me" + variation('affirmation'))
                    elif sequence('down', 'up'):
                        send_quick_chat("OH SNAP! Hey there, " + variation('friend'))
                    elif sequence('left', 'up'):
                        send_quick_chat("Nice shot! Or was that a great pass? Either way, " + variation('compliment').lower())
                    elif sequence('right', 'up'):
                        send_quick_chat("Centering! Just kidding, " + variation('foe').lower())
                    elif sequence('left', 'right'):
                        send_quick_chat("Thanks! It was totally accidental, of course, my " + variation('friend') )
                    elif sequence('left', 'down'):
                        send_quick_chat("HA! " + variation('Celebration').lower())
                    elif sequence('left', 'left'):
                        send_quick_chat(variation('Acknowledgment').capitalize())
                    elif sequence('up', 'right'):
                        send_quick_chat(variation('Confidence Boost').capitalize())
                    elif sequence('up', 'left'):
                        send_quick_chat("Need boost! Seriously, I'm always running on empty, sorry " + variation('friend'))
                    elif sequence('down', 'right'):
                        send_quick_chat("No problem. I mean, it might be your fault, " + variation('foe').lower())
                    elif sequence('down', 'left'):
                        send_quick_chat(variation('Apology').capitalize())
                    elif sequence('right', 'left'):
                        send_quick_chat(variation('compliment').capitalize())
                    elif sequence('right', 'right'):
                        send_quick_chat(variation('Encouraging Taunt').capitalize())
                    elif sequence('right', 'down'):
                        send_quick_chat(" " + variation('Challenge').lower())
                    elif sequence('down', 'down'):
                        send_quick_chat(variation('cat fact').capitalize())
    except Exception as e:
        print(e)
        break
