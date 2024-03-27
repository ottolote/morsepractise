import random
import pygame
import numpy
import math
import threading

# Initialize pygame
pygame.init()

# List of simple words to send in Morse code
WORDS = [
    'EAT', 'PIE', 'YUM', 'TASTY', 'SWEET', 
    'APPLE', 'BERRY', 'CHERRY', 'DATE', 'FIG', 'GRAPE', 'KIWI', 'LEMON', 'MANGO', 'OLIVE',
    'PEACH', 'PEAR', 'PLUM', 'PRUNE', 'QUINCE', 'RAISIN', 'APRICOT', 'BANANA', 'CARROT',
    'LETTUCE', 'ONION', 'POTATO', 'RADISH', 'SPINACH', 'TOMATO', 'TURNIP', 'CUCUMBER',
    'BEET', 'CELERY', 'GARLIC', 'JALAPENO', 'KALE', 'MELON', 'NECTARINE', 'PAPAYA',
    'PUMPKIN', 'RASPBERRY', 'WATERMELON', 'ZUCCHINI', 'BLUEBERRY', 'CABBAGE', 'EGGPLANT',
    'HONEYDEW', 'KIWIFRUIT', 'LYCHEE', 'MANDARIN', 'ORANGE', 'PARSNIP', 'PEANUT', 'PINEAPPLE',
    'RUTABAGA', 'SHALLOT', 'TAPIOCA', 'YAM', 'ARTICHOKE', 'BROCCOLI', 'CAULIFLOWER',
    'FENNEL', 'GUAVA', 'HORSERADISH', 'JICAMA', 'KOHLRABI', 'LIME', 'MUSHROOM', 'OKRA',
    'PERSIMMON', 'QUINOA', 'RHUBARB', 'SCALLION', 'SQUASH', 'TEFF', 'WALNUT', 'CHESTNUT',
    'ALMOND', 'CASHEW', 'DATEPIT', 'ELDERBERRY', 'FLAXSEED', 'GRAPEFRUIT', 'HAZELNUT',
    'JUNIPER', 'KUMQUAT', 'LOGANBERRY', 'MACADAMIA', 'NECTAR', 'OREGANO', 'PEPPER',
    'SESAME', 'SUNFLOWER', 'THYME', 'VANILLA', 'WHEAT', 'YEAST', 'BASIL', 'CORIANDER',
    'DILL', 'FENUGREEK', 'GINGER', 'HOP', 'JASMINE', 'LAVENDER', 'MARJORAM', 'NUTMEG',
    'OREGON', 'PAPRIKA', 'ROSEMARY', 'SAGE', 'TARRAGON', 'VERBENA', 'WILDRICE', 'XANTHAN',
    'YARROW', 'ZEST'
]

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..'
}

# Configurations for the beep sound
FREQUENCY = 1000  # 1kHz frequency for the beep
WPM = 22  # Words per minute
DOT_LENGTH = int(1200 / WPM)  # Duration of a dot in milliseconds, based on the standard word "PARIS"
DASH_LENGTH = DOT_LENGTH * 3  # Duration of a dash in milliseconds
WORD_SPACE = DOT_LENGTH * 7  # Space between words in milliseconds

# Initialize Pygame mixer with a specific frequency and channels
pygame.mixer.init(frequency=44100, channels=2)

# Constants for the sine wave generation
SAMPLE_RATE = 44100
VOLUME = 32767     # Max volume for signed 16-bit

def make_sound(frequency, duration):
    # Calculate the number of frames
    num_frames = int(SAMPLE_RATE * duration)
    # Generate the sine wave
    sine_wave = [int(VOLUME * math.sin(2 * math.pi * frequency * t / SAMPLE_RATE)) for t in range(num_frames)]
    # Convert to stereo by duplicating the frames
    stereo_wave = numpy.array([sine_wave, sine_wave], dtype=numpy.int16).T
    # Ensure the array is contiguous
    if not stereo_wave.flags['C_CONTIGUOUS']:
        stereo_wave = numpy.ascontiguousarray(stereo_wave, dtype=numpy.int16)
    # Make and return the Pygame sound object
    return pygame.sndarray.make_sound(stereo_wave)

def play_morse_code(word, callback=None):
    sound_sequence = []
    dot_sound = make_sound(FREQUENCY, DOT_LENGTH / 1000.0)
    dash_sound = make_sound(FREQUENCY, DASH_LENGTH / 1000.0)

    for letter in word.upper():
        for symbol in MORSE_CODE_DICT[letter]:
            if symbol == '.':
                sound_sequence.append((dot_sound, DOT_LENGTH))
            elif symbol == '-':
                sound_sequence.append((dash_sound, DASH_LENGTH))
            sound_sequence.append((None, DOT_LENGTH))  # Pause between symbols
        sound_sequence.append((None, DASH_LENGTH * 3 - DOT_LENGTH))  # Pause between letters
    sound_sequence.append((None, WORD_SPACE - DASH_LENGTH))  # Space between words

    def play_sequence(sequence):
        for sound, duration in sequence:
            if sound:
                sound.play()
            pygame.time.delay(duration)
        if callback:
            callback()

    # Start a new thread to play the sound sequence
    thread = threading.Thread(target=play_sequence, args=(sound_sequence,))
    thread.start()


class MorseGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Learn Morse Code')
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.round_number = 1
        self.total_time_start = pygame.time.get_ticks()
        self.total_letters_typed = 0
        self.in_menu = True  # Game starts in menu phase

    def start_new_round(self):
        self.display_word = random.choice(WORDS)
        self.input_word = ''
        self.start_time = pygame.time.get_ticks()
        self.in_result_phase = False
        play_morse_code(self.display_word)
        self.update_display()

    def update_display(self):
        self.screen.fill((0, 0, 0))
        if self.in_menu:
            self.draw_menu()
        else:
            self.draw_metrics()
            self.draw_input_and_result()
        pygame.display.flip()

    def draw_menu(self):
        menu_text = "Press ENTER to Start"
        menu_surface = self.small_font.render(menu_text, True, (255, 255, 255))
        menu_x = (self.screen.get_width() - menu_surface.get_width()) // 2
        menu_y = (self.screen.get_height() - menu_surface.get_height()) // 2
        self.screen.blit(menu_surface, (menu_x, menu_y))

    def draw_metrics(self):
        time_spent = (pygame.time.get_ticks() - self.start_time) / 1000
        total_time_elapsed = (pygame.time.get_ticks() - self.total_time_start) / 1000
        average_time_per_round = total_time_elapsed / self.round_number
        average_time_per_letter = total_time_elapsed / self.total_letters_typed if self.total_letters_typed > 0 else 0
        metrics = [
            (f"Time: {time_spent:.2f}", 10),
            (f"Total Time: {total_time_elapsed:.2f}", 36),
            (f"Avg/Round: {average_time_per_round:.2f}", 62),
            (f"Avg/Letter: {average_time_per_letter:.2f}", 88),
            (f"Round: {self.round_number}", 114)
        ]
        for _, (text, y_position) in enumerate(metrics):
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_position))

    def draw_input_and_result(self):
        base_y = 300
        if self.in_result_phase:
            for i, char in enumerate(self.display_word):
                color = (0, 255, 0) if i < len(self.input_word) and char == self.input_word[i] else (255, 0, 0)
                char_surface = self.font.render(char, True, color)
                self.screen.blit(char_surface, (10 + i * 35, base_y))

        for i, char in enumerate(self.input_word):
            char_surface = self.font.render(char, True, (255, 255, 255))
            self.screen.blit(char_surface, (10 + i * 35, base_y + 40))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                return self.handle_keydown_events(event)
        return True

    def handle_keydown_events(self, event):
        if self.in_menu:
            if event.key == pygame.K_RETURN:
                self.in_menu = False
                self.start_new_round()
            return True
        if event.key == pygame.K_ESCAPE:
            return False
        elif event.key == pygame.K_TAB:
            play_morse_code(self.display_word)
        elif event.key == pygame.K_RETURN:
            self.handle_return_key()
        elif event.key == pygame.K_BACKSPACE and not self.in_result_phase:
            self.input_word = self.input_word[:-1]
        elif not self.in_result_phase:
            self.input_word += event.unicode.upper()
        return True

    def handle_return_key(self):
        if not self.in_result_phase:
            self.in_result_phase = True
        else:
            if self.input_word == self.display_word:
                self.round_number += 1
                self.total_letters_typed += len(self.input_word)
            self.start_new_round()

    def run(self):
        running = True
        while running:
            self.update_display()
            running = self.handle_events()
            self.clock.tick(30)
        pygame.quit()

def game():
    morse_game = MorseGame()
    morse_game.run()

if __name__ == "__main__":
    game()
