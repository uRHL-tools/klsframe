import re


def safe_input(validations=None, prompt=None, error_msg=None, confirm=False, allow_empty=True):
    """Reads input from terminal, performing some security checks on the input

    Arguments:
        :param validations: Set of RegExp indicating the possible values of the input
        :param prompt: Custom text to be displayed before reading the input
        :param error_msg: Custom text to be displayed when input does not match valid regex
        :param confirm: Enables/Disables the prompt confirmation after entering a value
        :param allow_empty:
    """
    if validations is None:
        validations = []
    elif type(validations) is not list:
        validations = [validations]

    if error_msg is None:
        error_msg = "Error. Invalid input"
    if prompt is None:
        prompt = "Please introduce a value"
    while True:
        inval = input(f"{prompt}:\t")
        if not allow_empty and inval == "":
            print(error_msg)
        elif len(validations) > 0:
            for valid in validations:
                if re.fullmatch(valid, inval):
                    return inval
            print(f'{error_msg}')
        else:
            # TODO: enable confirmation
            return inval


def selectable_list(*args, placeholder=None, custom_prompt=None, enable_custom=False, allow_empty=True, verbose=False):
    """placeholder is a function or lambda that indicates what placeholder should be used for each item
    If nothing is specified the string representation of the item is printed
    Arguments:
    Examples
    tcp_sc = selectable_list(scan_policy.tcp_scans(), placeholder=lambda x: f"Custom prefix {x}")
    recon_sc = selectable_list(scan_policy.recon_scans(), 'An additional scan')
    TODO: Update doc
    TODO: enable/disable empty input in custom promtp
    TODO: quizas la lista pueda ser una lista doble [[descripcion de la opcion, valor]]
    """
    if placeholder is None:
        placeholder = lambda x: x
    else:
        enable_custom = True
    aux = []
    while True:
        counter = 0
        print(f'Available options\n>\n  0. Cancel operation')
        for elem in args:
            if type(elem) == list:
                for i in elem:
                    counter += 1
                    print(f'  {counter}. {placeholder(i)}')
                    aux.append(i)
            else:
                counter += 1
                print(f'  {counter}. {placeholder(elem)}')
                aux.append(elem)
        # Add the custom option in the end. Maybe is better at the beginning?
        if enable_custom:
            counter += 1
            print(f'  {counter}. Custom value')
        print(f'>')
        try:
            selection = int(input(f'\nPlease select one:\t'))
            if selection == 0:
                print(f'Operation canceled. Exiting...')
                exit(0)
            elif selection not in range(1, counter + 1):
                raise IndexError()
            else:
                if enable_custom and selection == counter:
                    if custom_prompt is None:
                        if allow_empty:
                            return {"index": counter, "value": safe_input(allow_empty=True)}
                        else:
                            return {"index": counter, "value": safe_input(allow_empty=False)}
                    else:
                        return {"index": counter, "value": custom_prompt()}
                else:
                    # return args[selection - 1]
                    if verbose:
                        print(f"You selected: ({selection}) {aux[selection - 1]}")
                    return {'index': selection - 1, "value": aux[selection - 1]}
        except ValueError:
            print(f'Error. Option not recognized')
        except IndexError:
            print(f'Error. Option out of bounds. Please select a number within the list')


class PromptForm:
    def __init__(self, title='untitled', desc=''):
        self.title = str(title)
        self.description = str(desc)
        self.fields = []
        self.last_result = {}

    def __str__(self):
        return f"PromptForm('{self.title}')"

    def show_info(self):
        print(f"---< Form '{self.title}' >---\n{self.description}\n---------")
        for f in self.fields:
            print(f"- {f}")

    def add_field(self, name, description='', example='', ftype='string', regex=None, nullable=False, defaultval=''):
        self.fields.append(FormField(name=name, description=description, example=example, ftype=ftype, regex=regex,
                                     nullable=nullable, defaultval=defaultval))

    def add_string_field(self):
        pass

    def add_numeric_field(self, decimal_digits=2, decimal_separator='.'):
        pass

    def add_list_field(self, separator=','):
        pass

    def reset(self):
        self.last_result.clear()

    def fill_in(self, compact_mode=True):
        input_form = {}
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
                field_num += 1
            else:
                raise TypeError("Invalid field type. Only cli.FormField allowed")
        self.last_result.update(input_form)
        return input_form


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
