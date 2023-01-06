import klsframe.cli.cli as cli


def test_prompt_form_simple():
    form = cli.PromptForm(title='Test 1', desc='Just a test. Or not. I don\'t care')
    form.add_field('nombre', nullable=False)
    form.add_field('apellidos', nullable=False)
    res = form.fill_in()
    print(res)
    assert res == form.last_result
    assert 'nombre' in res and 'apellidos' in res
    print('[OK] Test prompt_form_simple_test succeeded\n\n')


def test_prompt_form_advanced():
    form = cli.PromptForm(title='Test 2', desc='Just a test. Or not. I don\'t care')
    form.add_field(name='Nombre', description='Nombre del titular de la cuenta', example='Pedro')
    form.add_field(name='Apellidos', description='Apellidos del titular de la cuenta', example='Pérez')
    form.add_field(name='Edad', description='Edad en años del titular de la cuenta', example='12', ftype='number',
                   regex='[0-9]{1,3}')
    form.add_field('hobbies', ftype='list')
    # form.show_info()
    res = form.fill_in(compact_mode=False, confirm=True)
    print(res)
    assert res == form.last_result
    assert 'Nombre' in res and 'Apellidos' in res and 'Edad' in res
    print('[OK] Test prompt_form_advanced_test succeeded\n\n')


def test_confirm():
    print(cli.confirm_yes_no("Delete all assets", default=False, allow_empty=False, shortened=False))
    print(cli.confirm_yes_no("Exit", default=True, allow_empty=True, shortened=True))
    print(cli.confirm_yes_no("Eres tonoto?"))


def test_safe_input():
    age1 = input("Age")
    age2 = cli.safe_input("Age", )


def test_menu1():
    def cagar():
        print('prffrfffrf')

    def comer():
        print('ñamñam')

    def dormir():
        print('zZzzZZZzZzzZZz')

    men = cli.Menu(allowcustom=True)
    men.add_entry('cagar', 'Ir al trono', cagar)
    men.add_entry('comer', 'Monchear', comer)
    men.add_entry('dormir', 'Sobarla', dormir)
    print(men.open())


def test_menu2():
    dict_port_listing = {"Por defecto (no se especifican puertos)": "",
                         "Todos los puertos": "-p-",
                         "1000 puertos comunes": "--top-ports 1000"}
    menu1 = cli.Menu(allowcustom=True)
    menu1.add_entries(dict_port_listing)
    print(menu1.open())


def test_menu3():
    menu_options1 = [
        {'value': '', 'description': 'Por defecto (no se especifican puertos)'},
        {'value': '-p-', 'description': 'Todos los puertos'},
        {'value': '--top-ports 1000', 'description': '1000 puertos comunes'}
    ]

    def input_port():
        prompt = f"Introduce tu propia seleccion de puertos, separados por espacio (23 80 443) o un rango (0-1024)"
        range_regex = '^[0-9]{1,5}-[0-9]{1,5}$'
        listing_regex = '^(([0-9]{1,5})+[ ]?)+$'
        return cli.safe_input(validations=[range_regex, listing_regex], allow_empty=False, prompt=prompt)

    menu2 = cli.Menu(allowcustom=True, customprompt=input_port)
    menu2.add_entries(menu_options1)
    print(menu2.open())


if __name__ == '__main__':
    # test_confirm()
    # test_prompt_form_simple()
    test_prompt_form_advanced()
    # test_dict_to_table()
    # pyautogui.prompt(text="Apellido", title="field 1/3", default="mondongo")
