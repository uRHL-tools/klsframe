import klsframe.klsframe.cli as cli


def prompt_form_simple_test():
    form = cli.PromptForm(title='Test 1', desc='Just a test. Or not. I don\'t care')
    form.add_field('nombre', nullable=False)
    form.add_field('apellidos', nullable=False)
    res = form.fill_in()
    print(res)
    assert res == form.last_result
    assert 'nombre' in res and 'apellidos' in res
    print('[OK] Test prompt_form_simple_test succeeded\n\n')


def prompt_form_advanced_test():
    form = cli.PromptForm(title='Test 2', desc='Just a test. Or not. I don\'t care')
    form.add_field(name='Nombre', description='Nombre del titular de la cuenta', example='Pedro')
    form.add_field(name='Apellidos', description='Apellidos del titular de la cuenta', example='Pérez')
    form.add_field(name='Edad', description='Edad en años del titular de la cuenta', example='12', ftype='number',
                   regex='[0-9]{1,3}')
    form.add_field('hobbies', ftype='list')
    form.show_info()
    res = form.fill_in(compact_mode=False)
    print(res)
    assert res == form.last_result
    assert 'Nombre' in res and 'Apellidos' in res and 'Edad' in res
    print('[OK] Test prompt_form_advanced_test succeeded\n\n')


if __name__ == '__main__':
    prompt_form_simple_test()
    prompt_form_advanced_test()
