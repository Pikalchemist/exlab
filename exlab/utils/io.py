from enum import Enum


class Colors(Enum):
    # HEADER = '\033[95m'
    # OKBLUE = '\033[94m'
    # OKGREEN = '\033[92m'
    # WARNING = '\033[93m'
    # FAIL = '\033[91m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    NORMAL = '\033[39m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    RESET = '\033[0m'


def shortid(instance, length=4):
    return str(id(instance))[-length:]
