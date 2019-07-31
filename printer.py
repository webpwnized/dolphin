from enum import Enum
import curses

class Level(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    SUCCESS = 3
    DEBUG = 4

class Printer:

    # ---------------------------------
    # "Private" static class variables
    # ---------------------------------
    __grey = 37
    __red = 91
    __green = 92
    __yellow = 93
    __blue = 94
    __magenta = 95
    __cyan = 96
    __white = 97
    __bold = "\033[1m"
    __not_bold = "\033[21m"
    __mVerbose: bool = False
    __mDebug: bool = False
    __mColorMap = {
        Level.INFO: __blue,
        Level.WARNING: __yellow,
        Level.ERROR: __red,
        Level.SUCCESS: __green,
        Level.DEBUG: __cyan
    }
    __mLevelMap = {
        Level.INFO: "[*] INFO: ",
        Level.WARNING: "[*] WARNING: ",
        Level.ERROR: "[*] ERROR: ",
        Level.SUCCESS: "[*] SUCCESS: ",
        Level.DEBUG: "[*] DEBUG: "
    }

    # ---------------------------------
    # "Public" static class variables
    # ---------------------------------
    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool):
        self.__mVerbose = pVerbose

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool):
        self.__mDebug = pDebug

    # ---------------------------------
    # public instance constructor
    # ---------------------------------
    #def __init__(self) -> None:
    #    self.__mVerbose: bool = False
    #    self.__mDebug: bool = False

    # ---------------------------------
    # private instance methods
    # ---------------------------------

    # ---------------------------------
    # public instance methods
    # ---------------------------------

    # ---------------------------------
    # public static class methods
    # ---------------------------------
    @staticmethod
    def print(pMessage: str, pLevel: Level) -> None:
        # Only print INFO and SUCCESS messages if verbose is true
        # Only print DEBUG messages if debug is true
        # Warning, Error are always printed
        if (pLevel in [Level.INFO, Level.SUCCESS]) and not Printer.verbose: return None
        if (pLevel in [Level.DEBUG]) and not Printer.debug: return None
        print("\033[1;{}m{}{}\033[21;0m".format(Printer.__mColorMap[pLevel], Printer.__mLevelMap[pLevel], pMessage))

    @staticmethod
    def print_example_usage():
        print("""
Test connectivity to Rapid7 Open Data API\n
\tpython3 dolphin.py --verbose --test
\tpython3 byepass.py -v -t
\nDisplay Rapid7 Open Data API quota\n
\tpython3 dolphin.py --verbose --quota
\tpython3 byepass.py -v -q
\nList available Rapid7 Open Data studies\n
\tpython3 dolphin.py --verbose --list-studies
\tpython3 byepass.py -v -l
\nUpdate database using available Rapid7 Open Data studies\n
\tpython3 dolphin.py --verbose --update-studies
\tpython3 byepass.py -v -u
    """)