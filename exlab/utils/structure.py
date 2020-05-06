

def get_sub_dict_path(dict_: dict, keypath: str) -> (dict, str):
    keypath = keypath.replace('/', '.')
    path = keypath.split('.')
    while len(path) > 1:
        key = path.pop(0)
        dict_ = dict_[key]
    return (dict_, path[0])


def get_dict_path(dict_: dict, keypath: str):
    dict_, key = get_sub_dict_path(dict_, keypath)
    return dict_[key]


def set_dict_path(dict_: dict, keypath: str, value):
    dict_, key = get_sub_dict_path(dict_, keypath)
    dict_[key] = value
