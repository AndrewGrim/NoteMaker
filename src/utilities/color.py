import typing


class COLOR:
    """
    Stores colors as its attributes.\n
    Just preface your text with a color attribute and add "COLOR.END" after your text to clear the color.

    Example:\n
            print(f"{COLOR.RED}red text{COLOR.END}")
    """

    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    LIGHT_GREEN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    

class STYLE:
    """
    Stores styles as its attributes.\n
    Just preface your text with a style attribute and add "STYLE.END" after your text to clear the style.

    Example:\n
            print(f"{STYLE.BOLD}red text{STYLE.BOLD}")
    """

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def fail(message: str) -> None:
    """
    Prints "FAILURE!" followed by the message in red.
    """

    print(f"{COLOR.RED}FAILURE! {message}{COLOR.END}")


def warn(message: str) -> None:
    """
    Prints "WARNING!" followed by the message in yellow.
    """

    print(f"{COLOR.YELLOW}WARNING! {message}{COLOR.END}")


def ok(message: str) -> None:
    """
    Prints the message in green.
    """

    print(f"{COLOR.GREEN}{message}{COLOR.END}")


def info(message: str) -> None:
    """
    Prints the message in blue.
    """

    print(f"{COLOR.BLUE}{message}{COLOR.END}")


def debugPrint(message: str) -> None:
    """
    Prints "DEBUG:" followed by a newline and the message in purple.\n
    Used internally by debug().
    """

    print(f"{COLOR.PURPLE}\nDEBUG:\n{message}{COLOR.END}")