import sys
import time
import random
import pyautogui
from tkinter import Tk
import re
import keyboard
import signal

import guiLayout

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


class Action:
    def __init__(self):
        self.command = ''  # click, move, write, press...
        self.target = ''  # (x,y)
        self.value = ''  # Additional args, e.g. [right, triple] -> click
        self.description = ''  # Optional short description of the action.


class Worker:
    __MAX_SPEED = 2.0
    __MIN_SPEED = 0.0

    def __init__(self, speed=None):
        _allowed = ["autobot", "millennial", "grandpa"]
        if re.match('[0-9]+(.[0-9])?', speed) is not None:
            speed = float(speed)
            if self.__MAX_SPEED < speed or speed < self.__MIN_SPEED:
                raise ValueError('Invalid speed range for the Worker')
        elif type(speed) is str:
            if speed in _allowed:
                speed = float(_allowed.index(speed))
            else:
                raise ValueError(f'Unknown Worker speed profile "{speed}". '
                                 f'Supported profiles (from slow to fast) are: {", ".join(_allowed)}')

        self.speed_profile = speed
        self._interval_delay = 0.0
        self.busy = False  # Indicate if the worker is currently executing a subroutine
        self.target_window = ''
        self.gui_layout = guiLayout.GUILayout()
        # STATS
        self.traveling_time = 0
        self.total_clicks = 0
        self.total_keys_pressed = 0

        self.update_speed_profile(0)
        keyboard.add_hotkey('ctrl+alt+add', lambda: self.update_speed_profile(0.5))
        keyboard.add_hotkey('ctrl+alt+subtract', lambda: self.update_speed_profile(-0.5))
        keyboard.add_hotkey('ctrl+alt+p', self.halt_resume_execution)

    def update_speed_profile(self, inc):
        if 0.0 <= self.speed_profile + float(inc) <= 2.0:
            self.speed_profile += float(inc)
            # TODO: this formula may be improved
            self._interval_delay = (0.05 + self.speed_profile / 10) * (self.speed_profile + 1)
            pyautogui.PAUSE = self.speed_profile
            print(f"[INFO] Speed profile updated (fastest <= current <= slowest): 0 <= {self.speed_profile} <= 2")
        elif self.speed_profile == 0.0:
            print('[WARN] Already using the slower speed profile')
        elif self.speed_profile == 2.0:
            print('[WARN] Already using the fastest speed profile')
        else:
            raise ValueError("Error. Speed profile out of bounds")

    def _pre_actions_checks(self):
        self.find_target_window()
        if not self.busy:
            exit(0)

    def is_target_window(self):
        return re.search(self.target_window, pyautogui.getActiveWindow().title) is not None

    def find_target_window(self):
        if self.is_target_window():
            pyautogui.getActiveWindow().maximize()
        else:
            Worker.find_window(self.target_window)

    def halt_resume_execution(self):
        self.busy = not self.busy
        # ret = pyautogui.confirm(title='Halt execution', text='Execution halted. Do you want to continue?')
        # if ret == 'OK':
        #     p.resume()
        #     return
        # elif ret == 'Cancel':
        #     p.terminate()
        #     sys.exit(0)
        # else:
        #     raise ValueError('Unexpected error in function halt()')
        signal.raise_signal(signal.SIGTERM)
        raise KeyboardInterrupt

    def execute(self, **kwargs):
        # TODO: wrapper for every action execution, so that if busy is et to false, it will stop immediately
        self._pre_actions_checks()
        while self.busy:
            pass

    # --------------------------------------------------------------------------
    # BASIC API CALLS
    # --------------------------------------------------------------------------

    def click(self, x=None, y=None, button='left', clicks=1):
        self.busy = True
        self._pre_actions_checks()
        _allowed = ['left', 'middle', 'right']
        if button not in _allowed:
            raise ValueError(f'Invalid button argument for click(). Allowed values are: {", ".join(_allowed)}')
        else:
            # TODO implement the rest of the validations for the args: x, y and clicks
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=self._interval_delay)
        self.busy = False

    def move(self, x, y):
        self.busy = True
        self._pre_actions_checks()
        self.traveling_time += self.speed_profile
        pyautogui.moveTo(x, y, self.speed_profile, pyautogui.easeOutQuad)
        self.busy = False

    def write(self, msg):
        """
        Tries to write wherever the cursor is placed

        Arguments
            msg. String to be written. Can contain special characters (\n, \t...)
            If msg is a list of strings, then each element of the list will be written in a new line
        """
        self.busy = True
        self._pre_actions_checks()
        if type(msg) is str:
            pyautogui.write(message=msg, interval=self._interval_delay / 2)
            self.total_keys_pressed += len(msg)
        elif type(msg) is list:
            for m in msg:
                pyautogui.write(message=f'{m}\n', interval=self._interval_delay / 2)
                self.total_keys_pressed += len(m) + 1  # len(m) + \n
        else:
            raise TypeError('Invalid type for msg in write()')
        self.busy = False

    def press(self, *args):
        """
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
        self.busy = True
        self._pre_actions_checks()
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
                self.total_keys_pressed += len(_key.split('+')) * _presses
            else:
                pyautogui.press(keys=_key, presses=_presses, interval=self._interval_delay)
                self.total_keys_pressed += _presses
        self.busy = False

    def scroll(self, value, direction='vertical', x=None, y=None):
        """
        pyautogui.scroll(10)   # scroll up 10 "clicks"
        pyautogui.scroll(-10)  # scroll down 10 "clicks"
        pyautogui.scroll(10, x=100, y=100)  # move mouse cursor to 100, 200, then scroll up 10 "clicks"

        ONLY in OS X and Linux platforms
        pyautogui.hscroll(10)   # scroll right 10 "clicks"
        pyautogui.hscroll(-10)   # scroll left 10 "clicks"
        """
        self.busy = True
        self._pre_actions_checks()
        _allowed_directions = ['vertical', 'horizontal']
        _allowed_values = range(-10000, 10001)
        if direction not in _allowed_directions:
            raise ValueError(f"Error. Invalid value for direction ({direction})")
        elif direction == 'horizontal' and sys.platform.find('win') != -1:
            raise ValueError(f"Error. Horizontal scrolling not supported on Windows platform")
        elif value not in _allowed_values:
            raise ValueError(f"Error. Invalid scroll value. Valid range [-100, 100]")

        if direction == 'vertical':
            self.vt_scroll(clicks=value, x=x, y=y)
        elif direction == 'horizontal':
            self.hz_scroll(clicks=value, x=y, y=y)
        else:
            raise RuntimeError('Unexpected value for argument "direction"')
        self.busy = False

    @staticmethod
    def hz_scroll(clicks, x=None, y=None):
        if x is not None and y is not None:
            if guiLayout.safe_coordinates(x, y):
                pyautogui.hscroll(clicks=clicks, x=x, y=y)
            else:
                raise ValueError(f"Error. Coordinates ({x}, {y}) out of range")
        else:
            pyautogui.hscroll(clicks=clicks)

    @staticmethod
    def vt_scroll(clicks, x=None, y=None):
        if x is not None and y is not None:
            if guiLayout.safe_coordinates(x, y):
                pyautogui.vscroll(clicks=clicks, x=x, y=y)
            else:
                raise ValueError(f"Error. Coordinates ({x}, {y}) out of range")
        else:
            pyautogui.vscroll(clicks=clicks)

    def pause(self, seconds):
        self.traveling_time += seconds
        time.sleep(seconds)

    # --------------------------------------------------------------------------
    # ADVANCED FUNCTIONS
    # --------------------------------------------------------------------------

    def keep_awake(self):
        self.busy = True
        while self.busy:
            self.move(x=self.gui_layout.screen_center()[0] + random.randint(-200, 200),
                      y=self.gui_layout.screen_center()[1] + random.randint(-200, 200))
            self.press('f5', 'esc')
            self.busy = True

    def quick_action(self, action):
        # TODO: Implement quick actions
        pass

    def with_hold_do(self, holds=None, actions=None):
        """
        We can define here quick actions. For example 'ctrl-click', 'ctrl-cmd', 'shift-cmd'

        Arguments
            holds: e.g. 'ctrl', 'shift', 'alt', 'alt-gr', 'fn'...
            actions: a list of actions
                keys 'a', 'b', 'c'...
                clicks {'clicks': 1, button: 'left', 'x': x, 'y': y}
                    If (x, y) == (-1, -1) click in the current position
        """
        self.busy = True
        self._pre_actions_checks()
        if holds is None:
            holds = []
        if actions is None:
            actions = []
        with pyautogui.hold(holds):
            for act in actions:
                if type(act) is tuple and len(act) == 2:
                    self.click(x=act[0], y=act[1])
                    self.total_clicks += 1
                elif type(act) is dict:
                    self.click(button=act['button'], clicks=act['clicks'], x=act['x'], y=act['y'])
                elif type(act) is str:
                    self.write(act)
                    self.total_keys_pressed += 1
                else:
                    raise ValueError(f'Invalid type {type(act)} for hold_and_do(). ')
                self.pause(self.speed_profile)
        self.busy = False

    def copy_text(self, x=None, y=None, remove_special_chars=False):
        # TODO: refactor
        if x is None or y is None:
            x = pyautogui.position()[0]
            y = pyautogui.position()[1]
        self.move(x, y)
        pyautogui.click(button='left', clicks=3, interval=self._interval_delay)
        self.with_hold_do(['ctrl'], ['c'])
        if remove_special_chars:
            return re.sub('[\t\n\r]+', '', self.get_clipboard()).strip()
        else:
            return self.get_clipboard().strip()

    # --------------------------------------------------------------------------
    # STATIC FUNCTIONS
    # --------------------------------------------------------------------------

    @staticmethod
    def get_clipboard():
        # https://stackoverflow.com/questions/101128/how-do-i-read-text-from-the-clipboard
        return Tk().clipboard_get()

    @staticmethod
    def set_clipboard(data):
        Tk().clipboard_clear()
        Tk().clipboard_append(data)

    @staticmethod
    def get_coordinates():
        while True:
            elem_name = pyautogui.prompt('Place the cursor on the component and enter its name')
            if elem_name == '' or elem_name is None:
                break
            else:
                time.sleep(5)
                pos = pyautogui.position()
                print(f'{elem_name} = ({pos[0]}, {pos[1]})')

    @staticmethod
    def find_window(target):
        for wd in pyautogui.getAllTitles():
            if re.search(target, wd) is not None:
                windows = pyautogui.getWindowsWithTitle(w)
                if windows is None:
                    raise FileNotFoundError(f"Window {target} not found. Is it open?")
                elif len(windows) != 1:
                    raise ValueError(f"Ambiguous search. More than one window with name {target}")
                else:
                    windows[0].activate()
                    windows[0].maximize()
                    return windows[0]
        raise FileNotFoundError(f"Window {target} not found. Is it open?")


# -----------------------------------------------------------------------------------------------------------------
# ------------------------------------- MAIN-----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # center = (pyautogui.size().width / 2, pyautogui.size().height / 2)
    center = (800, 300)
    w = Worker('millennial')
    # quick_actions['win_explorer']()
    print(w.__dict__)
    w.keep_awake()
    exit(0)
    time.sleep(5)
    w.click(x=center[0], y=center[1])
    for i in range(0, 3):
        w.scroll(500)
        time.sleep(1)
        w.scroll(-500)
