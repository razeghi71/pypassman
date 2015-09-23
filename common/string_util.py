import string
from evdev import ecodes
import random

def random_word(length=6):
    return ''.join(random.choice(string.digits + string.ascii_lowercase)
                   for i in range(length))


def get_char_by_code(code):
    str_char = ecodes.bytype[ecodes.EV_KEY][code]

    if len(str_char) == 5:
        return string.lower(str_char[4:])
    elif len(str_char) == 7:
        return str_char[6:]
    return str_char