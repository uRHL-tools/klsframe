import json
import os
import re

import pyautogui
import worker


def safe_coordinates(x, y):
    if x is None or y is None:
        return False
    else:
        return not (x <= 0 or pyautogui.size().width <= x or y <= 0 or pyautogui.size().height <= y)


def screen_center():
    return pyautogui.size().width / 2, pyautogui.size().height / 2


class GUILayout:
    """
    A GUI Layout is a list of pages.
    """

    def __init__(self):
        self.name = ''
        self.screen_size = pyautogui.size()
        self.pages = []

    def __eq__(self, other):
        if other is None or len(self.pages) != len(other.pages):
            return False
        for pg_i, pg_j in zip(self.pages, other.pages):
            if pg_i.name != pg_j.name:
                return False
            if pg_i.components != pg_j.components:
                return False
        return True

    def get(self, comp_name, pg_name=None):
        for pg in self.pages:
            if pg_name is not None and pg_name != pg.name:
                continue
            for k, v in pg.components.items():
                if k == comp_name:
                    return v
        return None

    def new_page(self, page_name):
        _new = GUIPage(page_name)
        self.pages.append(_new)
        return _new

    def add_component(self, page_name, comp_name, x, y):
        for pg in self.pages:
            if pg.name == page_name:
                pg.components[comp_name] = (x, y)
                return
        _new_pg = self.new_page(page_name)
        _new_pg.components[comp_name] = (x, y)
        return

    def to_json(self):
        _res = []
        counter = -1
        for pg in self.pages:
            counter += 1
            _res.append({pg.name: {}})
            for comp, comp_coors in pg.components.items():
                _res[counter][pg.name][comp] = [comp_coors[0], comp_coors[1]]
        return _res

    @staticmethod
    def load(source):
        _gly = GUILayout()
        # TODO: load from a json file/object
        if type(source) is list:
            for src in source:
                _new_pg = _gly.new_page("".join(src.keys()))
                for comp_name, comp_coords in src[_new_pg.page_name].items():
                    _gly.add_component(_new_pg.page_name, comp_name, x=comp_coords[0], y=comp_coords[1])
        elif type(source) is str and os.path.isfile(source):
            with open(source, 'r') as file:
                return GUILayout.load(json.load(file))
        elif type(source) is str:
            # TODO: implement JSON string parsing
            pass
        else:
            raise ValueError("Invalid object type for load()")
        return _gly

    def local_save(self, outfile):
        with open(outfile, 'w') as file:
            json.dump(self.to_json(), file, indent=2)

    def verify(self):
        for pg in self.pages:
            for comp, comp_coords in pg.components.items():
                if not safe_coordinates(comp_coords[0], comp_coords[0]):
                    print(f"ERROR. Coordinate verification failed. Coordinates of component '{comp}' are not valid")
                    return 1
        return 0

    # START TABLE FUNCTIONS
    def get_table_row_at(self, tname, rownum):
        pass

    def get_table_row_with(self, tname, filters):
        pass

    def get_table_all_rows(self, tname):
        pass

    # END TABLE FUNCTIONS

    def screen_center(self):
        return self.screen_size.width / 2, self.screen_size.height / 2


class GUIPage:
    def __init__(self, pgname):
        self.page_name = str(pgname)
        self.transitions = []
        self.components = []
        self.tables = []

    def __repr__(self):
        return self.__dict__


class GUITransition:
    # TODO
    pass


class GUIComponent:
    def __init__(self, name, comptype, x, y):
        _allowed_types = ['button', 'input']
        self.comp_name = name
        if str(comptype.lower()) in _allowed_types:
            self.comp_type = str(comptype.lower())
        else:
            raise TypeError(f"Invalid type ({type}) for GUIComponent")
        self.x = x
        if safe_coordinates(x, y):
            self.x = x
            self.y = y
        else:
            raise ValueError(f"Invalid coordinates ({(x, y)}")


class GUITable:
    def __init__(self):
        self.table_name = ''
        self.first_row_Y = 0.0
        self.row_height = 0.0
        self.table_size = 0  # Num of rows
        self.columns = []

    def get_row_at(self, index):
        if index == 0:
            return self.headers()
        elif 0 < index <= self.table_size:
            # TODO
            offset = (index - 1) * self.row_height
            row = {}
            for col in self.columns:
                # A human will just read the columns, but the app need to copy the text to get it
                # Thus those clicks do not count for Worker.stats
                a = GUITableColumn()
                w = worker.Worker()
                content = w.copy_text(x=col.left_side_X(), y=self.first_row_Y + offset)
                if a.validate(content):
                    row[col.col_name] = content
                else:
                    raise ValueError(f"Unexpected value ({content}) for column '{col.col_name}'")
            return row
        else:
            raise IndexError(f"Index {index} out of bounds [0, {self.table_size}]")

    def get_row_where(self, **kwargs):
        pass

    def headers(self):
        return [col.col_name for col in self.columns]


class GUITableColumn:
    def __init__(self):
        self.col_name = ''
        self.left_border_x = -1.0
        self.right_border_x = -1.0
        self.regex = None

    def center_X(self):
        return self.left_border_x + self.width() / 2

    def width(self):
        return self.right_border_x - self.left_border_x

    def left_side_X(self):
        return self.left_border_x + (self.width() * 0.15)

    def right_side_X(self):
        return self.right_border_x - (self.width() * 0.15)

    def validate(self, value):
        if self.regex is None or re.fullmatch(self.regex, value) is not None:
            return True
        else:
            return False
