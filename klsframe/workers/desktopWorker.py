import random
import re
import signal
import time
import keyboard
import pyautogui
import autobot
import klsframe.gui.guiLayout as guiLayout


def click_on(elem: guiLayout.GUIComponent, button='left', clicks=1):
    pt = elem.get_point(position='center')
    click_at(pt, button=button, clicks=clicks)


def click_at(point: guiLayout.Point, button='left', clicks=1):
    autobot.click(x=point.x, y=point.y, button=button, clicks=clicks)


def move_to(self, point: guiLayout.Point):
    pyautogui.moveTo(point.x, point.y, duration=self.speed_profile, tween=pyautogui.easeOutQuad)


# --------------------------------------------------------------------------
# CLASSES
# --------------------------------------------------------------------------

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

    def is_target_window(self, alert=False):
        if re.search(self.target_window, pyautogui.getActiveWindow().title) is not None:
            return True
        else:
            if alert:
                res = pyautogui.confirm('WINDOW OUT OF SCOPE. Press enter to continue...')
                if res == 'Cancel':
                    print('[INFO] Operation cancelled by the user. Exiting...')
                    exit(0)
            return False

    def find_target_window(self):
        if self.is_target_window():
            pyautogui.getActiveWindow().maximize()
        else:
            autobot.find_window(self.target_window)

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
        # TODO: wrapper for every action execution, so that if busy is set to false, it will stop immediately
        self._pre_actions_checks()
        while self.busy:
            pass

    def click(self, x=None, y=None, button='left', clicks=1):
        self.busy = True
        self._pre_actions_checks()
        autobot.click(x=x, y=y, button=button, clicks=clicks, interval=self._interval_delay)
        self.busy = False

    def move(self, x, y):
        self.busy = True
        self._pre_actions_checks()
        self.traveling_time += self.speed_profile
        autobot.move(x, y, self.speed_profile)
        self.busy = False

    def move_to(self, point: guiLayout.Point):
        self.busy = True
        self._pre_actions_checks()
        self.traveling_time += self.speed_profile
        pyautogui.moveTo(point.x, point.y, self.speed_profile, pyautogui.easeOutQuad)
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
            autobot.write(msg=msg, interval=self._interval_delay / 2)
            self.total_keys_pressed += len(msg)
        elif type(msg) is list:
            for m in msg:
                autobot.write(msg=f'{m}\n', interval=self._interval_delay / 2)
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

    def pause(self, seconds):
        self.traveling_time += seconds
        autobot.pause(seconds)

    # --------------------------------------------------------------------------
    # ADVANCED FUNCTIONS
    # --------------------------------------------------------------------------

    def keep_awake(self, minutes=None):
        self.busy = True
        if minutes is None:
            stop_condition = True
        elif isinstance(minutes, int) and 1 <= minutes < 1440:  # Between 1 minute and 1 day
            _end = time.time() + minutes * 60
            stop_condition = lambda: time.time() <= _end
        else:
            raise ValueError("Value provided for the parameter 'minutes' is out of range [1, 1440]")
        while stop_condition:
            autobot.move(x=self.gui_layout.screen_center()[0] + random.randint(-200, 200),
                         y=self.gui_layout.screen_center()[1] + random.randint(-200, 200))
            autobot.press('f5', 'esc')
            time.sleep(2)

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


# -----------------------------------------------------------------------------------------------------------------
# ------------------------------------- MAIN-----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    autobot.keep_awake(minutes=15)
    # w = Worker('millennial')
    # print(w.__dict__)
    # w.keep_awake(minutes=1)
    # exit(0)
