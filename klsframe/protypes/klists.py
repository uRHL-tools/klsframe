from typing import Optional


def split_list(full_list: list, chunk_size: int, verbose=False):
    """
    Splits a list in chunks of `chunk_size` elements

    :param full_list: list to be split
    :param chunk_size: size of each chunk
    :param verbose: Enable/disable verbose output
    :return: a list of lists, containing all the chunks obtained from `full_list`
    """
    if not isinstance(chunk_size, int) or chunk_size < 1:
        raise ValueError("Unexpected value for parameter 'chunk_size'. Only positive integer numbers allowed")
    aux = []
    offset = 0
    step = 0
    while offset < len(full_list):
        aux.append(full_list[offset: offset + chunk_size])
        step += 1
        offset = chunk_size * step
    if verbose:
        for ind, chunk in enumerate(aux, 1):
            print(f"[INFO] Chunk {ind} ({len(chunk)}): {chunk}")
    return aux


def cast_list(clist, to, _from=None):
    """
    :except NameError: `to` is not defined (unknown type)
    :param clist: list to be cast
    :param to: type to which the elements are cast
    :param _from: if not None, only the elements of this type are cast
    :return: The same list but with the cast values
    """
    assert isinstance(clist, list)
    if _from is None:
        return [to(elem) for elem in clist]
    else:
        return [(to(elem) if isinstance(elem, _from) else elem) for elem in clist]


def list_wrap(obj):
    """
    Checks if the given ``obj`` is a list before returning it.
    If not, it will wrap the object and include it in a list

    :param obj: Object or value to be tested
    :return: a list including the provided ``obj``, or ``obj`` itself, if it already was a list
    """
    return obj if isinstance(obj, list) else [obj]


def equivalent(l1: list, l2: list):
    if not isinstance(l1, list) or not isinstance(l2, list):
        raise TypeError("Invalid parameter types. Only list allowed")
    elif len(l1) != len(l2):
        return False
    else:
        for item in l1:
            if item not in l2:
                return False
        return True


def shuffle(lt):
    import random
    import copy
    _aux = copy.deepcopy(lt)
    random.shuffle(_aux)
    return _aux


def merge(*args, how=None) -> Optional[list]:
    #TODO
    if len(args) == 1:
        print("[WARN] Not enough list to merge (less than one)")
        return args[0]
    else:
        res = []
        for i in range(0, len(args)):
            res.extend([f"{a} {b}" for a, b in zip(res, args[i])])


if __name__ == '__main__':
    pass
