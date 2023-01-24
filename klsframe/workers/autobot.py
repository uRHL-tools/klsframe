import sys
import time
import random
import re
import pyautogui
import pyperclip


# --------------------------------------------------------------------------
# BASIC API CALLS
# --------------------------------------------------------------------------

def safe_coordinates(x, y):
    if x is None or y is None:
        return False
    else:
        return not (x <= 0 or pyautogui.size().width <= x or y <= 0 or pyautogui.size().height <= y)


def click(x=None, y=None, button='left', clicks=1, interval=0.0):
    """
    Moves to (x, y) and clicks the specified button ``clicks`` times
    :param x:
    :param y:
    :param button:
    :param clicks:
    :param interval:
    :return:
    """
    pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)


def move(x, y, duration=0.0):
    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)


def write(msg, interval=0.0):
    """
    Tries to write wherever the cursor is placed

    Arguments
        msg. String to be written. Can contain special characters (\n, \t...)
        If msg is a list of strings, then each element of the list will be written in a new line
    """
    if type(msg) is str:
        pyautogui.write(message=msg, interval=interval)
    elif type(msg) is list:
        for m in msg:
            pyautogui.write(message=f'{m}\n', interval=interval)
    else:
        raise TypeError('Invalid type for msg in write()')


def press(*args, interval=0.0):
    """
    Combination of pyautogui.press and pyautogui.hotkey
    press('ctrl', 'c') = press(*['ctrl', 'c']) = press('ctrl+c')
    You can pass a list of key-actions that will be executed in order, for example: 'ctrl+c', 'ctrl+v'
    Arguments (2 types)
        string
             'a' -> single press
             'a+b+c' -> hotkey (use \\ to escape +, like 3\\+2 = 5)
        tuple
            ('c', 2) -> {'key': 'c', 'presses': 2}
            ('ctrl+t', 2) -> {'key': 'ctrl+t', 'presses': 2}
    """
    for arg in args:
        if type(arg) is tuple:
            _key = arg[0]
            _presses = arg[1]
        elif type(arg) is str:
            _key = arg
            _presses = 1
        else:
            raise TypeError('Invalid args type in press() ')

        if _key.find('+') != -1 and re.search('^\\w+(\\+\\w+)+', arg) is not None:
            for _i in range(0, _presses):
                pyautogui.hotkey(*_key.split('+'))
        else:
            pyautogui.press(keys=_key, presses=_presses, interval=interval)


def scroll(value, direction='vertical', x=None, y=None):
    """
    pyautogui.scroll(10)   # scroll up 10 "clicks"
    pyautogui.scroll(-10)  # scroll down 10 "clicks"
    pyautogui.scroll(10, x=100, y=100)  # move mouse cursor to 100, 200, then scroll up 10 "clicks"

    ONLY in OS X and Linux platforms
    pyautogui.hscroll(10)   # scroll right 10 "clicks"
    pyautogui.hscroll(-10)   # scroll left 10 "clicks"
    """
    _allowed_directions = ['vertical', 'horizontal']
    _allowed_values = range(-10000, 10001)
    if direction not in _allowed_directions:
        raise ValueError(f"Error. Invalid value for direction ({direction})")
    elif direction == 'horizontal' and sys.platform.find('win') != -1:
        raise ValueError(f"Error. Horizontal scrolling not supported on Windows platform")
    elif value not in _allowed_values:
        raise ValueError(f"Error. Invalid scroll value. Valid range [-100, 100]")

    if direction == 'vertical':
        vt_scroll(clicks=value, x=x, y=y)
    elif direction == 'horizontal':
        hz_scroll(clicks=value, x=y, y=y)
    else:
        raise ValueError('Unexpected value for argument "direction"')


def hz_scroll(clicks, x=None, y=None):
    if x is not None and y is not None:
        if safe_coordinates(x, y):
            pyautogui.hscroll(clicks=clicks, x=x, y=y)
        else:
            raise ValueError(f"Error. Coordinates ({x}, {y}) out of range")
    else:
        pyautogui.hscroll(clicks=clicks)


def vt_scroll(clicks, x=None, y=None):
    if x is not None and y is not None:
        if safe_coordinates(x, y):
            pyautogui.vscroll(clicks=clicks, x=x, y=y)
        else:
            raise ValueError(f"Error. Coordinates ({x}, {y}) out of range")
    else:
        pyautogui.vscroll(clicks=clicks)


def pause(seconds):
    time.sleep(seconds)


# --------------------------------------------------------------------------
# ADVANCED FUNCTIONS
# --------------------------------------------------------------------------

def keep_awake(minutes=None):
    screen = pyautogui.size()
    safe_threshold = 25
    delay = 2
    if minutes is None:
        stop_condition = lambda: True
    elif isinstance(minutes, int) and 1 <= minutes < 1440:  # Between 1 minute and 1 day
        _end = time.time() + minutes * 60
        stop_condition = lambda: time.time() <= _end
    else:
        raise ValueError("Value provided for the parameter 'minutes' is out of range [1, 1440]")
    while stop_condition():
        # TODO: use my own click function
        pyautogui.moveTo(
            x=random.randint(safe_threshold, screen.width - safe_threshold),
            y=random.randint(safe_threshold, screen.height - safe_threshold))
        if random.randint(0, 3) == 1:  # 25% chances
            pyautogui.press('f5')
            time.sleep(delay)
            pyautogui.press('esc')
            time.sleep(delay)
        else:
            time.sleep(delay)


def quick_action(action):
    # TODO: Implement quick actions
    quick_actions = {
        'next_window': lambda: pyautogui.hotkey(*['alt', 'tab']),
        'next_tab': lambda: pyautogui.hotkey(*['ctrl', 'tab']),
        'close_tab': lambda: pyautogui.hotkey(*['ctrl', 'w']),
        'win_explorer': lambda: pyautogui.hotkey(*['win', 'e']),
        'cut': {'hold': ['ctrl'], 'do': ['x']},
        'open-link-new-tab': {'hold': ['ctrl'], 'do': [{'button': 'left', 'presses': 1, 'x': -1, 'y': -1}]},
        'copy': ['ctrl', 'c'],
        'paste': ['ctrl', 'v'],
    }
    # These are predefined quick actions
    # (right) click
    # double (right) click
    # triple (right) click
    # left click
    # middle click
    __PREDEFINED_ACTIONS = [
        {
            'command': 'press',
            'target': (None, None),
            'value': ['ctrl', 'c'],
            'description': 'copy'
        }
    ]
    pass


def with_hold_do(holds=None, actions=None):
    """
    We can define here quick actions. For example 'ctrl-click', 'ctrl-cmd', 'shift-cmd'

    Arguments
        holds: e.g. 'ctrl', 'shift', 'alt', 'alt-gr', 'fn'...
        actions: a list of actions
            keys 'a', 'b', 'c'...
            clicks {'clicks': 1, button: 'left', 'x': x, 'y': y}
                If (x, y) == (-1, -1) click in the current position
    """
    if holds is None:
        holds = []
    if actions is None:
        actions = []
    with pyautogui.hold(holds):
        for act in actions:
            if type(act) is tuple and len(act) == 2:
                click(x=act[0], y=act[1])
            elif type(act) is dict:
                click(button=act['button'], clicks=act['clicks'], x=act['x'], y=act['y'])
            elif type(act) is str:
                write(act)
            else:
                raise ValueError(f'Invalid type {type(act)} for hold_and_do(). ')


def copy_text(x=None, y=None, remove_special_chars=False):
    # TODO: refactor
    if x is None or y is None:
        x = pyautogui.position()[0]
        y = pyautogui.position()[1]
    # move(x, y)
    pyautogui.click(x=x, y=y, button='left', clicks=3)
    with_hold_do(['ctrl'], ['c'])
    if remove_special_chars:
        return re.sub('[\t\n\r]+', '', get_clipboard()).strip()
    else:
        return get_clipboard().strip()


def get_clipboard():
    # https://stackoverflow.com/questions/101128/how-do-i-read-text-from-the-clipboard
    # return Tk().clipboard_get()
    return pyperclip.paste()


def set_clipboard(data):
    # https://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard
    # TODO: fix. It does not work with Tkinter
    pyperclip.copy(str(data))


def get_coordinates():
    # TODO: Update according to the new class ScreenArea
    while True:
        elem_name = pyautogui.prompt('Place the cursor on the component and enter its name')
        if elem_name == '' or elem_name is None:
            break
        else:
            time.sleep(5)
            pos = pyautogui.position()
            print(f'{elem_name} = ({pos[0]}, {pos[1]})')


def find_window(target):
    for wd in pyautogui.getAllTitles():
        if re.search(target, wd) is not None:
            windows = pyautogui.getWindowsWithTitle(wd)
            if windows is None:
                raise FileNotFoundError(f"Window {target} not found. Is it open?")
            elif len(windows) != 1:
                raise ValueError(f"Ambiguous search. More than one window with name {target}")
            else:
                windows[0].activate()
                windows[0].maximize()
                return windows[0]
    raise FileNotFoundError(f"Window {target} not found. Is it open?")
