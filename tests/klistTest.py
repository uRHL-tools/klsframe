import klsframe.protypes.klists as _klists


def test_cast_list():
    numeros = list(range(0, 15))
    variety = [1, 2, 3, 'hola', 'adios']
    print(_klists.cast_list(numeros, float))
    print(_klists.cast_list(variety, float, _from=int))
    try:
        print(_klists.cast_list(variety, float))
        print(f"[INFO] ``test_cast_list`` failed. Exception expected")
    except ValueError:
        print(f"[INFO] Exception catched\n[INFO] ``test_cast_list`` successful")


def test_equivalent():
    assert _klists.equivalent([1, 2, 3], [1, 2, 3]) is True
    assert _klists.equivalent([3, 1, 2], [1, 2, 3]) is True
    assert _klists.equivalent(["aba", 2, 3], [2, "aba", 3]) is True
    assert _klists.equivalent(["aba", 2, 3], [2, "aba", 2]) is False
    assert _klists.equivalent(["aba", 2, 3], [2, "aba"]) is False
    assert _klists.equivalent([{'nombre': 'manolo'}, 2, "aba"], [2, "aba", {'nombre': 'manolo'}]) is True
    assert _klists.equivalent([{'nombre': 'manolo', 'apellidos': 'bombo'}, 2], [2, {'nombre': 'manolo'}]) is False
    try:
        print(_klists.equivalent("variety", [1, 2, 3]))
        print(f"[INFO] ``test_equivalent`` failed. Exception expected")
    except TypeError:
        print(f"[INFO] Exception catched\n[INFO] ``test_equivalent`` successful")

if __name__ == '__main__':
    test_cast_list()
    test_equivalent()
