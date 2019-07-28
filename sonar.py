from printer import Printer, Level
import urllib.request
import urllib.error
import json

class Sonar:

    # ---------------------------------
    # "Private" static class variables
    # ---------------------------------
    __cAPI_KEY_HEADER: str = "X-Api-Key"
    __cBASE_URL: str = "https://us.api.insight.rapid7.com/opendata/"
    __cQUOTA_URL: str = ''.join([__cBASE_URL, "quota/"])
    __cSTUDIES_URL: str = ''.join([__cBASE_URL, "studies/"])

    __mAPIKey: str = ""
    __mDebug: bool = False
    __mVerbose: bool = False
    __mPrinter: Printer = Printer

    # ---------------------------------
    # "Public" static class variables
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

    # ---------------------------------
    # public instance constructor
    # ---------------------------------
    def __init__(self) -> None:
        self.__mVerbose: bool = False
        self.__mDebug: bool = False
        self.__mPrinter.verbose = False
        self.__mPrinter.debug = False
        self.__do_common_init_tasks()

    def __init__(self, pVerbose: bool, pDebug: bool) -> None:
        self.__mVerbose: bool = pVerbose
        self.__mDebug: bool = pDebug
        self.__mPrinter.verbose = pVerbose
        self.__mPrinter.debug = pDebug
        self.__do_common_init_tasks()

    def __do_common_init_tasks(self):
        self.__parse_api_key()

    # ---------------------------------
    # private instance methods
    # ---------------------------------
    def __parse_api_key(self) -> None:
        self.__mPrinter.print("Reading Rapid7 Open API key", Level.INFO)
        with open('rapid7-open-api.key') as lKeyFile:
            self.__mAPIKey = lKeyFile.readline()
        self.__mPrinter.print("Rapid7 Open API key: {}".format(self.__mAPIKey), Level.INFO)

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

    # ---------------------------------
    # public instance methods
    # ---------------------------------
    def test_connectivity(self) -> None:
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)

    def check_quota(self) -> None:
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        lJSON = json.loads(lHTTPResponse.read().decode('utf-8'))
        Printer.print("{}/{} requests used in last {} hours".format(
            lJSON['quota_used'],lJSON['quota_allowed'],int(int(lJSON['quota_timespan'])/3600)), Level.INFO
        )

    def list_studies(self) -> None:
        lHTTPResponse = self.__connect_to_open_data_api(self.__cSTUDIES_URL)
        lJSON = json.loads(lHTTPResponse.read().decode('utf-8'))
        #print(lJSON)
        for item in lJSON:
            #for key, value in item.items():
            #    print(key,value)
            print("{} {}".format(item['uniqid'],item['name']))
            print("Updated: {}".format(item['updated_at']))
            #print("File set: {}".format(item['sonarfile_set']))
            print("\t{}".format(item['long_desc']))
            print()

    # ---------------------------------
    # public static class methods
    # ---------------------------------