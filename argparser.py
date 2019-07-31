from printer import Printer, Level
import config as Config

class Parser:

    __mArgs = None
    __mConfiguration: Config = None
    __mDebug: bool = False
    __mVerbose: bool = False
    __mTestConnectivity: bool = False
    __mCheckQuota: bool = False
    __mShowExamples: bool = False
    __mListStudies: bool = False
    __mUpdateStudies: bool = False
    __mRapid7OpenAPIKeyFilePath: str = ""
    __mStudiesOfInterest: list = []
    __mDatabaseFilename: str = ""
    __mPrinter: Printer = Printer

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool) -> None:
        self.__mDebug = pDebug
        self.__mPrinter.debug = pDebug

    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool) -> None:
        self.__mVerbose = pVerbose
        self.__mPrinter.verbose = pVerbose

    @property  # getter method
    def show_examples(self) -> bool:
        return self.__mShowExamples

    @property  # getter method
    def test(self) -> bool:
        return self.__mTestConnectivity

    @property  # getter method
    def quota(self) -> bool:
        return self.__mCheckQuota

    @property  # getter method
    def list_studies(self) -> bool:
        return self.__mListStudies

    @property  # getter method
    def update_studies(self) -> bool:
        return self.__mUpdateStudies

    @property  # getter method
    def rapid7_open_api_key_file_path(self) -> str:
        return self.__mRapid7OpenAPIKeyFilePath

    @property  # getter method
    def studies_of_interest(self) -> list:
        return self.__mStudiesOfInterest

    # Constructor Method
    def __init__(self: object, pArgs, pConfig: Config) -> None:
        self.__mArgs = pArgs
        self.__mConfiguration = pConfig
        self.__mVerbose = self.__mArgs.verbose
        self.__mTestConnectivity = self.__mArgs.test
        self.__mCheckQuota = self.__mArgs.quota
        self.__parse_arg_debug()
        self.__mShowExamples = self.__mArgs.examples
        self.__mListStudies = self.__mArgs.list_studies
        self.__mUpdateStudies = self.__mArgs.update_studies
        self.__mRapid7OpenAPIKeyFilePath = self.__mConfiguration.RAPID7_OPEN_API_KEY_FILE_PATH
        self.__mStudiesOfInterest = self.__mConfiguration.STUDIES_OF_INTEREST
        self.__mDatabaseFilename = self.__mConfiguration.DATABASE_FILENAME

    # private methods
    def __parse_arg_debug(self) -> None:
        if self.__mArgs.debug:
            self.__mDebug = self.__mArgs.debug
        else:
            self.__mDebug = self.__mConfiguration.DEBUG