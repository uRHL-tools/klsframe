import re
from typing import Union

import klsframe.gui.gui as klsgui
from klsframe.utilities.utils import validate, text_padding, dict_to_table


def confirm_yes_no(selection, default=True, allow_empty=True, shortened=True):
    a = 'yes'
    b = 'no'
    if shortened:
        a = 'y'
        b = 'n'
    if isinstance(default, bool) and default:
        hint = f'[{a.upper()}/{b}]'
    elif isinstance(default, bool) and not default:
        hint = f'[{b.upper()}/{a}]'
    else:
        raise ValueError("Unexpected value for parameter 'default'")
    while True:
        opt = input(
            f"You selected:\n{text_padding(selection, decorator='*', decorate_lines='first')}\n"
            f">> Do you want to continue? {hint}\t").strip().lower()
        if opt == '':
            if allow_empty:
                return default
            else:
                print("Please provide an answer")
        elif re.match('(no|n)', opt):
            return False
        elif re.match('(yes|y)', opt):
            return True
        else:
            print(f"Option '{opt}' not recognized")


def safe_input(validations=None, prompt=None, error_msg=None, confirm=False, allow_empty=True):
    """
    Safe input for string values. Reads input from terminal, performing some security checks on the input

    Arguments:
        :param validations: Set of RegExp indicating the possible values of the input, like a whitelist
        :param prompt: Custom text to be displayed before reading the input
        :param error_msg: Custom text to be displayed when input does not match valid regex
        :param confirm: Enables/Disables the prompt confirmation after entering a value
        :param allow_empty: Allow/Disallow empty as input
    """
    # Validate the parameters
    if validations is None:
        validations = []
    if error_msg is None:
        error_msg = "Error. Invalid input"
    if prompt is None:
        prompt = "Please introduce a value"
    while True:
        inval = input(f"{prompt}:\t")
        if not allow_empty and inval == "":
            print(f"{error_msg} (Input cannot be empty)")
        elif validate(inval, validations):
            if bool(confirm) and not confirm_yes_no(inval):  # Confirmation prompt enabled
                continue  # Confirmation: rejected. Continue the questioning loop
            else:  # Confirmation prompt disabled, or accepted
                return inval
        else:  # Validation failed
            print(f"{error_msg} (Validation failed)")


def safe_string_input():
    # TODO: safe_string_input(). Actually it is already implemented in safe_input()
    # Just apply regex
    pass


def safe_number_input(min_val=None, max_val=None, decimal_digits=0, decimal_sep='.', default=None) -> Union[int, float]:
    """
    Safe input for numeric values.

    :param min_val: Min value allowed. None (-infinite) by default
    :param max_val: Max value allowed. None (infinite) by default
    :param decimal_digits: Decimal digit count. 0 (default) for integer numbers.
        If not None, the input is rounded to ``decimal_digits``
    :param decimal_sep: Character used to separate the decimal part from the integer part.
        Allowed chars: '.' | ','. Note: decimal_sep = '.' <==> thousand_sep = ',' (and vice versa)
    :param default: Default value for the input. If not None, if the user inputs an empty value,
        the default value will be returned. If None, the user input cannot be empty
    :return: The validated and sanitized number input by the user
    """
    if decimal_sep == '.':
        thousand_sep = ','
    elif decimal_sep == ',':
        thousand_sep = '.'
    else:
        raise ValueError("Unexpected value for parameter 'decimal_sep'. Allowed: ,|.")
    bounds = f"[{min_val}, {max_val}]".replace('[None', '(-infinite').replace('None]', 'infinite)')
    # General number regex
    custom_regex = "^-?([0-9]{1,3}" + thousand_sep + ")*[0-9]+"
    if decimal_digits > 0:
        custom_regex += "(\\" + decimal_sep + "[0-9]+)?"
        _prompt = f'Please introduce an decimal number (up to {decimal_digits} decimal digits) within {bounds}'
    else:
        _prompt = f'Please introduce an integer number within {bounds}'
    # Check parameter `default`
    if default is None:
        _allow_empty = False
    else:
        _allow_empty = True
        custom_regex = f"({custom_regex})?"  # Include the empty input in the regex
        _prompt += f" [default: {default}]"  # Inform the user about the default value
    # Questioning loop
    while True:
        inval = safe_input(prompt=_prompt, validations=custom_regex, allow_empty=_allow_empty).replace(thousand_sep, '')
        if inval == '':  # If user input is empty, use the default value
            inval = default
        if decimal_digits > 0:
            inval = float(inval).__round__(decimal_digits)
        else:
            inval = int(inval)
        if (min_val is None or min_val <= inval) and (max_val is None or max_val >= inval):
            return inval
        else:
            print(f"[ERROR] Value out of bounds {bounds}")


def selectable_list(args: list, placeholder=None, custom_prompt=None, enable_custom=False, verbose=False):
    # I disabled the param allow_empty because if a custom opt is offered, the empty option should not be available,
    # If you want to offer an "empty" option, you should include it in the list
    # :param allow_empty:
    #       Enables/disables empty input. Only applied on custom inputs (when ``enable_custom`` is ``True``)
    """
    TODO: Update selectable_list() docstring
    Examples:
        tcp_sc = selectable_list(scan_policy.tcp_scans(), placeholder=lambda x: f"Custom prefix {x}")
        recon_sc = selectable_list(scan_policy.recon_scans(), 'An additional scan')

    :param args: List of things (object, list, dictionaries) to be listed
    :param placeholder: function or lambda that generates a custom string for each element of the list.
    If it is None the string representation of the item is used. The strings are used for the list representation
    :param custom_prompt: custom function that request an input and return a value
    :param enable_custom: Enables/disables the custom option
    :param verbose: True to increase verbosity. False by default
    :return: A dict like: {'index': index of the selected element within the list, 'value': element selected}
    """
    if placeholder is None:
        placeholder = lambda x: x
    if (enable_custom is None or enable_custom is False) and custom_prompt is not None:
        # In the case of providing a custom prompt, enabled_custom is supposed to be True
        enable_custom = True
    aux = []  # List used to expand the selectable list with Cancel and Custom options
    # Generate the printable prompt
    indent = ' ' * 2
    counter = 0
    printable_prompt = ['Available options', '>', f'{indent}0. Cancel operation', '>']
    for elem in args:
        if isinstance(elem, list):
            for i in elem:
                counter += 1
                printable_prompt.insert(-1, f'{indent}{counter}. {placeholder(i)}')
                aux.append(i)
        # Disabled because each dict item should not be selectable and independent of the rest of its sibling items
        # If you want to implement a ``selectable_dict`` create a ``Menu``
        # elif isinstance(elem, dict):
        #     for k, v in elem.items():
        #         counter += 1
        #         printable_prompt.insert(-1, f'{indent}{counter}. {placeholder(f"{k} ({v})")}')
        #         aux.append({k: v})
        else:
            counter += 1
            printable_prompt.insert(-1, f'{indent}{counter}. {placeholder(elem)}')
            aux.append(elem)
    # Add the custom option in the end. Maybe is better at the beginning?
    if enable_custom:
        counter += 1
        printable_prompt.insert(-1, f'{indent}{counter}. Custom value')
    while True:
        try:
            print("\n".join(printable_prompt))
            selection = int(input(f'\nPlease select one:\t'))
            if selection == 0:
                print(f'Operation canceled. Exiting...')
                exit(0)
            elif selection not in range(1, counter + 1):
                raise IndexError()
            else:
                if enable_custom and selection == counter:  # Custom option selected
                    # Counter = -1 => clarify that the (custom) option is not included in the list provided by the user
                    counter = -1
                    if custom_prompt is None:
                        value = safe_input(allow_empty=False)
                    else:
                        value = custom_prompt()
                else:  # Any other option selected
                    if verbose:
                        print(f"You selected: ({selection}) {aux[selection - 1]}")
                    counter = selection - 1  # Update counter to store the selected index
                    value = aux[selection - 1]
                break
        except ValueError:
            print(f'Error. Option not recognized')
        except IndexError:
            print(f'Error. Option out of bounds. Please select a number within the list')
    return {"index": counter, "value": value}


# --------------------------------------------------------------------------
# --------------------<| M E N U |>-----------------------------------------
# --------------------------------------------------------------------------
class MenuEntry:
    def __init__(self, val, desc=None, callback=None):
        self.value = str(val)
        if desc is not None:
            self.description = str(desc)
        else:
            self.description = None
        self.callback = callback

    def __str__(self):
        if self.description is not None and self.description != self.value:
            return f"'{self.value}' ({self.description})"
        else:
            return f"'{self.value}'"

    def __repr__(self):
        return str(self.value)


class Menu:
    def __init__(self, allowcustom=False, customprompt=None):
        self.entries = []
        self.allow_custom = allowcustom
        self.custom_prompt = customprompt

    def add_entry(self, value, description=None, callback=None):
        self.entries.append(MenuEntry(value, description, callback))

    def add_entries(self, iterable: Union[dict, list]):
        """

        :param iterable: a dict like {'option1 description': 'option1 value', opt2...}
            or a list of serialized (dictionaries) MenuEntry instances
        :return:
        """
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self.add_entry(v, k)
        elif isinstance(iterable, list):
            for elem in iterable:
                if 'description' in elem:
                    desc = elem['description']
                else:
                    desc = None
                if 'callback' in elem:
                    cb = elem['callback']
                else:
                    cb = None
                self.add_entry(elem['value'], description=desc, callback=cb)
        else:
            raise TypeError("Unexpected type for parameter 'iterable'. Allowed: dict | list")

    def open(self):
        ret = selectable_list(self.entries, enable_custom=self.allow_custom, custom_prompt=self.custom_prompt)
        if isinstance(ret['value'], MenuEntry) and ret['value'].callback is not None:
            ret['value'].callback()
        return ret


# --------------------------------------------------------------------------
# --------------------<| F O R M S |>---------------------------------------
# --------------------------------------------------------------------------

class FormField:
    def __init__(self, name, description='', example='', ftype='string', regex=None, nullable=False, defaultval=None):
        self.name = str(name)
        self.description = str(description)
        self.example = str(example)
        _allowed_types = ['string', 'number', 'list']
        if ftype in _allowed_types:
            self.ftype = str(ftype)
        else:
            raise ValueError(f"Invalid value for FormField.ftype. Allowed values are: {', '.join(_allowed_types)}")
        self.regex = regex
        if isinstance(nullable, bool):
            self.is_nullable = bool(nullable)
        else:
            raise TypeError("Invalid value for FormField.is_nullable. Only bool allowed")
        self.default_value = defaultval

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        name = self.name
        desc = self.description
        eg = self.example
        if self.description == '':
            desc = 'Description not provided'
        if self.example == '':
            eg = 'not provided'
        return f"'{name}': {desc}. (e.g.: {eg})"

    def long_str(self):
        name = self.name
        desc = self.description
        eg = self.example
        if self.description == '':
            desc = 'Not provided'
        if self.example == '':
            eg = 'Not provided'
        return f"  Title: {name}\n  Description: {desc}\n  Example: {eg}"

    def input(self):
        # while True:
        # TODO: use safe input to simplify the method and avoid code repetition
        return safe_input(
            validations=self.regex,
            prompt=f'>> {self.name} = ',
            error_msg=None,
            confirm=False,
            allow_empty=self.is_nullable
        )
        # inval = input(f'>> {self.name} = ')
        # if inval == '' and not self.is_nullable:
        #     print(f'[ERROR] This field cannot be empty and must match')
        #     continue
        # # Check field syntax
        # if self.regex is not None and re.fullmatch(self.regex, inval) is None:
        #     print(f'[ERROR] Invalid input syntax')
        #     continue
        # return inval


class StringFormField(FormField):
    def __init__(self, name, description='', example='', regex=None, nullable=False, defaultval=''):
        super().__init__(name=name, description=description, example=example, ftype='string', regex=regex,
                         nullable=nullable, defaultval=defaultval)

    def input(self):
        return str(super().input())


class NumberFormField(FormField):
    def __init__(self, name, description='', example='', regex=None, nullable=False, defaultval=0.0, decimal_digits=0,
                 decimal_separator='.', min_val=None, max_val=None):
        super().__init__(name=name, description=description, example=example, ftype='string', regex=regex,
                         nullable=nullable, defaultval=defaultval)
        self.decimal_digits = decimal_digits
        if min_val > max_val:
            raise ArithmeticError("Parameter 'min_val' is greater than 'max_val'")
        else:
            self.min_val = min_val
            self.max_val = max_val
        _allowed_separators = [',', '.']
        if decimal_separator in _allowed_separators:
            self.decimal_separator = decimal_separator
        else:
            raise ValueError("Unexpected value for the parameter 'decimal_separator'. Allowed: ',' | '.'")

    @property
    def regex(self):
        # Build regex from min_val, max_val, decimal_digits and decimal_separator
        custom_regex = "^"
        if self.min_val < 0 or self.max_val < 0:
            custom_regex += "-?"
        if self.max_val is None:
            custom_regex += "[0-9]+"
        else:
            custom_regex += "[0-9]{1," + str(
                len(str(self.max_val).replace('-', '').split(self.decimal_separator))) + "}"
        if self.decimal_digits > 0:
            custom_regex += f"(\\{self.decimal_separator}[0-9]" + "{1," + str(self.decimal_digits) + "})?"
        return custom_regex

    def input(self):
        inval = safe_input(
            validations=self.regex,
            prompt=f'>> {self.name} = ',
            error_msg="Error. Invalid input. Allowed: []",
            confirm=False,
            allow_empty=self.is_nullable
        )
        if self.decimal_digits > 0:
            inval = float(inval)
        else:
            inval = int(inval)
        if self.min_val <= inval <= self.max_val:
            return inval
        else:
            raise ValueError(f"Value out of range. Allowed: [{self.min_val}, {self.max_val}]")


class ListFormField(FormField):
    def __init__(self, name, description='', example='', regex=None, nullable=False, defaultval='', elem_separator=',',
                 max_len=None):
        super().__init__(name=name, description=description, example=example, ftype='string', regex=regex,
                         nullable=nullable, defaultval=defaultval)
        self.elem_separator = elem_separator
        self.max_len = max_len


class PromptForm:
    """
    Contrary to the class ``Menu``, which allows the user to select an option from a list,
    the Form class allows the user to input values
    """

    def __init__(self, title='untitled', desc=''):
        self.title = str(title)
        self.description = str(desc)
        self.fields = []
        self.last_result = {}
        # TODO: usar pandas
        # las columnas son los tries
        # Las filas los campos del formulario

    def __str__(self):
        return f"PromptForm('{self.title}')"

    def show_info(self):
        print(f"---< Form '{self.title}' >---\n{self.description}\n---------")
        for f in self.fields:
            print(f"- {f}")

    def get_summary_table(self):
        return f"\n----< Form '{self.title}' >----\n{dict_to_table(self.last_result)}"

    def add_field(self, name, description='', example='', ftype='string', regex=None, nullable=False, defaultval=''):
        _allowed_types = ['string', 'number', 'list']
        if ftype not in _allowed_types:
            raise ValueError(f"Unexpected value for paramter 'ftype'. Allowed: {', '.join(_allowed_types)}")
        if ftype == 'string':
            self.add_string_field(name=name, description=description, example=example, regex=regex,
                                  nullable=nullable, defaultval=defaultval)
        elif ftype == 'number':
            self.add_numeric_field()
        elif ftype == 'list':
            self.add_list_field()
        # self.fields.append(FormField(name=name, description=description, example=example, ftype=ftype, regex=regex,
        #                              nullable=nullable, defaultval=defaultval))

    def add_string_field(self, name, description='', example='', regex=None, nullable=False, defaultval=''):
        self.fields.append(StringFormField(name=name, description=description, example=example, regex=regex,
                                           nullable=nullable, defaultval=defaultval))

    def add_numeric_field(self, name, description='', example='', regex=None,
                          nullable=False, defaultval=0, decimal_digits=2, decimal_separator='.'):
        self.fields.append(NumberFormField(name=name, description=description, example=example, regex=regex,
                                           nullable=nullable, defaultval=defaultval, decimal_digits=decimal_digits,
                                           decimal_separator=decimal_separator))

    def add_list_field(self, name, description='', example='', regex=None,
                       nullable=False, defaultval='', separator=',', max_len=None):
        """

        :param name: Name of the form field
        :param description: Description of the form field
        :param example: Example of a valid value for the field
        :param regex: Regex to be matched against the user input
        :param nullable: Enables/disables a null/None/empty input
        :param defaultval: Default value for a list element
        :param separator: character used to separate the elements of the list. The comma (, ) is used by default
        :param max_len: maximum length of the list. None for no size restriction
        :return: A python list containing the input values
        """
        self.fields.append(ListFormField(name=name, description=description, example=example, regex=regex,
                                         nullable=nullable, defaultval=defaultval, elem_separator=separator,
                                         max_len=max_len))

    def reset(self):
        self.last_result.clear()

    def fill_in(self, compact_mode=True, confirm=False, gui=False):
        while True:
            input_form = {}
            if gui:
                klsgui.confirm_continue_or_exit(title=f"Form '{self.title}'", text=self.description,
                                                button_continue='Start')
            else:
                print(f"---< Form '{self.title}' >---")
            if not compact_mode:
                print(f"{self.description}\n{'-' * 20}")
            field_num = 0
            while True:
                if field_num >= len(self.fields):
                    break
                field = self.fields[field_num]
                if isinstance(field, FormField):
                    # Print field information
                    if compact_mode:
                        print(f"[Field {field_num + 1}/{len(self.fields)}] {field}")
                    else:
                        print(f"[Field {field_num + 1}/{len(self.fields)}]\n{field.long_str()}")
                    # Desde aqui
                    # input_form[field.name] = field.input()
                    inval = input(f'>> {field.name} = ')
                    if inval == '' and not field.is_nullable:
                        print(f'[ERROR] This field cannot be empty')
                        continue
                    # Check field syntax
                    if field.regex is None:
                        pass
                    elif re.fullmatch(field.regex, inval) is None:
                        print(f'[ERROR] Invalid input syntax')
                    # Check field type
                    if field.ftype == 'string':
                        input_form[field.name] = inval
                    elif field.ftype == 'number':
                        if inval.find('.') != -1:
                            input_form[field.name] = float(inval)
                        else:
                            input_form[field.name] = int(inval)
                    elif field.ftype == 'list':
                        input_form[field.name] = [val.strip() for val in inval.split(',')]
                    # hasta aqui
                    field_num += 1
                else:
                    raise TypeError("Invalid field type. Only cli.FormField allowed")
            self.last_result.update(input_form)
            if confirm:
                if confirm_yes_no(self.get_summary_table()):
                    break
                else:
                    continue
            else:
                break
        return input_form


# --------------------------------------------------------------------------
# --------------------<| M A I N |>-----------------------------------------
# --------------------------------------------------------------------------


if __name__ == '__main__':
    # Do some quick tests here
    pass



