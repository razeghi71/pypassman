from common.string_util import *
import sys

def get_input_from_reader(reader):
    read_string = ""
    for event in reader.read_loop():
        if event.value == 1 and event.type == 1:
            if event.code == 28:
                break
            else:
                key_pressed = get_char_by_code(event.code)
                if key_pressed != "KEY_BACKSPACE":
                    sys.stdout.write('*')
                    sys.stdout.flush()
                    read_string += key_pressed
                elif len(read_string) != 0:
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                    read_string = read_string[:-1]
    return read_string