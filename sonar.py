from printer import Printer, Level
from database import SQLite
import urllib.request
import urllib.error
import json
from datetime import datetime
from argparser import Parser

class Sonar:

    # ---------------------------------
    # "Private" class variables
    # ---------------------------------
    __cAPI_KEY_HEADER: str = "X-Api-Key"
    __cBASE_URL: str = "https://us.api.insight.rapid7.com/opendata/"
    __cQUOTA_URL: str = ''.join([__cBASE_URL, "quota/"])
    __cSTUDIES_URL: str = ''.join([__cBASE_URL, "studies/"])
    __SECONDS_PER_HOUR: int = 3600
    __cLAST_OCCURENCE: int = 1
    __cYEAR: int = 0
    __cMONTH: int = 1
    __cDAY: int = 2
    __cEPOCH_TIME: int = 3
    __cFILESET: int = 4
    __cPROTOCOL: int = 0
    __cPORT: int = 1

    __mAPIKey: str = ""
    __mDebug: bool = False
    __mVerbose: bool = False
    __mAPIKeyFile:str = ""
    __mStudiesOfInterest: list = []
    __mPrinter: Printer = Printer

    # ---------------------------------
    # "Public" class variables
    # ---------------------------------
    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool):
        self.__mVerbose = pVerbose
        self.__mPrinter.verbose = pVerbose

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool):
        self.__mDebug = pDebug
        self.__mPrinter.debug = pDebug

    @property  # getter method
    def api_key(self) -> str:
        return self.__mAPIKey

    @api_key.setter  # setter method
    def api_key(self: object, pAPIKey: str):
        self.__mAPIKey = pAPIKey

    @property  # getter method
    def api_key_file(self) -> str:
        return self.__mAPIKeyFile

    @api_key_file.setter  # setter method
    def api_key_file(self: object, pAPIKeyFile: str):
        self.__mAPIKeyFile = pAPIKeyFile

    @property  # getter method
    def studies_of_interest(self) -> list:
        return self.__mStudiesOfInterest

    @studies_of_interest.setter  # setter method
    def studies_of_interest(self: object, pStudiesOfInterest: list):
        self.__mStudiesOfInterest = pStudiesOfInterest

    # ---------------------------------
    # public instance constructor
    # ---------------------------------
    def __init__(self, p_parser: Parser) -> None:
        self.__mVerbose: bool = Parser.verbose
        self.__mDebug: bool = Parser.debug
        self.__mPrinter.verbose = Parser.verbose
        self.__mPrinter.debug = Parser.debug
        self.__mAPIKeyFile = Parser.rapid7_open_api_key_file_path
        self.__mStudiesOfInterest = Parser.studies_of_interest
        SQLite.database_filename = Parser.database_filename
        self.__parse_api_key()

    # ---------------------------------
    # private instance methods
    # ---------------------------------
    def __initialize_database(self) -> None:
        if not self.__verify_database_exists():
            self.__create_database()

    def __verify_database_exists(self) -> bool:
        return SQLite.verify_database_exists()

    def __create_database(self) -> None:
        SQLite.create_database()

    def __parse_api_key(self) -> None:
        self.__mPrinter.print("Reading Rapid7 Open API key", Level.INFO)
        with open(self.api_key_file) as lKeyFile:
            self.__mAPIKey = lKeyFile.readline()

    def __connect_to_open_data_api(self, pURL: str):
        self.__mPrinter.print("Connecting to Rapid7 Open API", Level.INFO)
        lHTTPRequest = urllib.request.Request(pURL)
        lHTTPRequest.add_header(self.__cAPI_KEY_HEADER, self.__mAPIKey)
        try:
            lHTTPResponse = urllib.request.urlopen(lHTTPRequest)
            self.__mPrinter.print("Connected to Rapid7 Open API", Level.SUCCESS)
            return lHTTPResponse
        except urllib.error.HTTPError as lHTTPError:
            self.__mPrinter.print("Cannot connect to Rapid7 Open API: {} {}".format(lHTTPError.code, lHTTPError.reason),
                                  Level.ERROR)
        except urllib.error.URLError as lURLError:
            self.__mPrinter.print("Cannot connect to Rapid7 Open API: {}".format(lURLError.reason), Level.ERROR)

    def __get_studies(self) -> list:
        # Open Data API --> studies
        # "uniqid","name","short_desc","long_desc","study_url","study_name","study_venue",
        # "study_bibtext","contact_name","contact_email","organization_name","organization_website",
        # "created_at","updated_at","sonarfile_set"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cSTUDIES_URL)
        return(json.loads(lHTTPResponse.read().decode('utf-8')))

    def __study_is_interesting(self, p_study: dict) -> bool:
        return(p_study['uniqid'] in self.studies_of_interest)

    def __print_study_metadata(self, pStudy: dict) -> None:
        # Open Data API --> studies
        # "uniqid","name","short_desc","long_desc","study_url","study_name","study_venue",
        # "study_bibtext","contact_name","contact_email","organization_name","organization_website",
        # "created_at","updated_at","sonarfile_set"
        Printer.print("Found study of interest", Level.SUCCESS)
        Printer.print("{} {}".format(pStudy['uniqid'], pStudy['name']), Level.INFO)
        Printer.print("Updated: {}".format(pStudy['updated_at']), Level.INFO)
        Printer.print("{}".format(pStudy['short_desc']), Level.INFO)
        Printer.print("{}".format(pStudy['long_desc']), Level.INFO)
        Printer.print("{} files are available".format(len(pStudy['sonarfile_set'])), Level.INFO)

    def __parse_study_filename(self, p_filename: str) -> None:
        lParts = p_filename.split('.')[0].split('-')
        print("Filename: {}".format(p_filename))
        print("Year: {}".format(lParts[self.__cYEAR]))
        print("Month: {}".format(lParts[self.__cMONTH]))
        print("Day: {}".format(lParts[self.__cDAY]))
        print("Timestamp: {}".format(datetime.fromtimestamp((float(lParts[self.__cEPOCH_TIME])))))

        l_protocol_port = lParts[self.__cFILESET].rsplit('_', self.__cLAST_OCCURENCE)
        if l_protocol_port.__len__() == 2 and str.isdigit(l_protocol_port[1]):
            Printer.print("Protocol: {}".format(l_protocol_port[0]), Level.INFO)
            Printer.print("Port: {}".format(l_protocol_port[1]), Level.INFO)
        elif l_protocol_port.__len__() == 2:
            Printer.print("Protocol: {} {}".format(l_protocol_port[0], l_protocol_port[1]), Level.INFO)
        elif l_protocol_port.__len__() == 1:
            Printer.print("Protocol: {}".format(l_protocol_port[0]), Level.INFO)
        else:
            Printer.print("Unexpected format: {}".format(l_protocol_port), Level.WARNING)



    # ---------------------------------
    # public instance methods
    # ---------------------------------
    def test_connectivity(self) -> None:
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)

    def check_quota(self) -> None:
        # Open Data API --> studies
        # "quota_allowed","quota_timespan","quota_used","quota_left","oldest_action_expires_in"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        l_studies = json.loads(lHTTPResponse.read().decode('utf-8'))
        Printer.print("{}/{} requests used in last {} hours".format(
            l_studies['quota_used'],l_studies['quota_allowed'],int(int(l_studies['quota_timespan'])/self.__SECONDS_PER_HOUR)), Level.INFO
        )

    def list_studies(self) -> None:
        l_studies = self.__get_studies()
        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study)

    def update_studies(self) -> None:

        self.__initialize_database()
        l_studies: list = self.__get_studies()

        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study)
                for l_filename in l_study['sonarfile_set']:
                    self.__parse_study_filename(l_filename)

    # ---------------------------------
    # public static class methods
    # ---------------------------------