from printer import Printer, Level
from database import SQLite
from database import StudyFileRecord
import urllib.request
import urllib.error
import shutil
import json
import gzip
from datetime import datetime
from argparser import Parser
import os

class Sonar:

    # ---------------------------------
    # "Private" class variables
    # ---------------------------------
    __cAPI_KEY_HEADER: str = "X-Api-Key"
    __cBASE_URL: str = "https://us.api.insight.rapid7.com/opendata/"
    __cQUOTA_URL: str = ''.join([__cBASE_URL, "quota/"])
    __cSTUDIES_URL: str = ''.join([__cBASE_URL, "studies/"])
    __cFILE_METADATA_BASE_URL: str = ''.join([__cBASE_URL, "studies/"])
    __cFILE_DOWNLOAD_BASE_URL: str = ''.join([__cBASE_URL, "studies/"])
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
    __m_days_until_study_too_old: int = 0
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
        self.__m_days_until_study_too_old = Parser.days_until_study_too_old
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

    def __print_study_filename_record(self, l_record: StudyFileRecord) -> None:
        print()
        Printer.print("Filename: {}, Protocol: {}, Port:{}, Timestamp: {}".format(l_record.filename,l_record.protocol,l_record.port,l_record.timestamp_string), Level.INFO)

    def __parse_study_filename(self, p_study: str, p_filename: str) -> StudyFileRecord:

        l_record = StudyFileRecord()
        l_parts = p_filename.split('.')[0].split('-')

        try:
            l_record.study_uniqid = p_study
            l_record.filename = p_filename
            l_record.year = l_parts[self.__cYEAR]
            l_record.month = l_parts[self.__cMONTH]
            l_record.day = l_parts[self.__cDAY]
            l_record.timestamp = l_parts[self.__cEPOCH_TIME]
            l_record.timestamp_string = datetime.fromtimestamp((float(l_parts[self.__cEPOCH_TIME])))

            l_protocol_port = l_parts[self.__cFILESET].rsplit('_', self.__cLAST_OCCURENCE)
            if l_protocol_port.__len__() == 2 and str.isdigit(l_protocol_port[1]):
                l_record.protocol = l_protocol_port[0]
                l_record.port =l_protocol_port[1]
            elif l_protocol_port.__len__() == 2:
                l_record.protocol = "".format(l_protocol_port[0], l_protocol_port[1])
                l_record.port = -1
            elif l_protocol_port.__len__() == 1:
                l_record.protocol = l_protocol_port[0]
                l_record.port = -1
            else:
                Printer.print("Unexpected format: {}".format(l_protocol_port), Level.WARNING)

            self.__print_study_filename_record(l_record)
            return l_record
        except IndexError as l_index_error:
            l_record = None
            Printer.print("Unexpected format: {} {} {}".format(l_index_error, p_filename, l_parts), Level.WARNING)

    def __format_file_size(self, p_file_size_bytes: int, p_suffix: str = 'B'):
        l_file_size: str = ""
        for l_unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(p_file_size_bytes) < 1024.0:
                return "{} {}{}".format(round(p_file_size_bytes,2), l_unit, p_suffix)
            p_file_size_bytes /= 1024.0

    def __get_study_file_information(self, p_study: str, p_filname: str) -> dict:
        # Open Data API --> studies/<study unique ID>/<filename>
        # "name", "fingerprint", "size (bytes)", "updated_at"
        Printer.print("Fetching metadata: study {}, file {}".format(p_study, p_filname), Level.INFO)
        l_file_metadata_url: str = "{}{}/{}/".format(self.__cFILE_METADATA_BASE_URL, p_study, p_filname)
        lHTTPResponse = self.__connect_to_open_data_api(l_file_metadata_url)
        l_file_metadata: dict = json.loads(lHTTPResponse.read().decode('utf-8'))
        Printer.print("File {}: fingerprint {}, {} bytes, updated at {}".format(l_file_metadata["name"],l_file_metadata["fingerprint"],self.__format_file_size(int(l_file_metadata["size"])),l_file_metadata["updated_at"]), Level.INFO)
        return l_file_metadata

    def __get_study_file_download_link(self, p_study: str, p_filname: str) -> str:
        # Open Data API --> studies/<study unique ID>/<filename>/download/
        # "url"
        Printer.print("Fetching study file download link: study {}, file {}".format(p_study, p_filname), Level.INFO)
        l_download_url: str = "{}{}/{}/download/".format(self.__cFILE_DOWNLOAD_BASE_URL, p_study, p_filname)
        lHTTPResponse = self.__connect_to_open_data_api(l_download_url)
        l_response: dict = json.loads(lHTTPResponse.read().decode('utf-8'))
        l_download_link: str = l_response['url']
        Printer.print("Fetched download link for file {} from study {}: {}".format(p_filname, p_study, l_download_link), Level.SUCCESS)
        return l_download_link

    def __get_available_sonar_files(self) -> list:
        l_studies: list = self.__get_studies()
        l_interesting_files = []

        Printer.print("Checking if any interesting Sonar files are available for download", Level.INFO)

        # if an interesting file is found in an interesting study, download the file metadata
        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study)
                for l_filename in l_study['sonarfile_set']:
                    l_sf_record: StudyFileRecord = self.__parse_study_filename(l_study['uniqid'], l_filename)
                    if l_sf_record:
                        l_interesting_files.append((l_sf_record.study_uniqid, l_sf_record.filename, l_sf_record.year, l_sf_record.month, l_sf_record.day, l_sf_record.timestamp, l_sf_record.timestamp_string, l_sf_record.protocol, l_sf_record.port))

        return l_interesting_files

    def __download_study_file(self, p_study, p_filename) -> str:
        WRITE_BYTES: str = 'wb'

        Printer.print("Downloading interesting study file: study {}, file {}".format(p_study, p_filename), Level.INFO)

        l_file_information: dict = self.__get_study_file_information(p_study, p_filename)
        l_download_link: str = self.__get_study_file_download_link(p_study, p_filename)
        l_local_filename: str = "/tmp/{}".format(p_filename)
        with urllib.request.urlopen(l_download_link) as l_http_response, open(l_local_filename, WRITE_BYTES) as l_output_file:
           shutil.copyfileobj(l_http_response, l_output_file)

        Printer.print("Downloaded file to {}".format(l_local_filename), Level.SUCCESS)

        #TODO: Keep track of files that are downloaded and parsed so we dont download them again in the future
        #TODO: Possibly calculate hash of downloaded file to make sure its legit

        return l_local_filename

    def __delete_study_file(self, p_local_filename: str) -> None:
        try:
            os.remove(p_local_filename)
        except OSError:
            pass

    # ---------------------------------
    # public instance methods
    # ---------------------------------
    def test_connectivity(self) -> None:
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)

    def check_quota(self) -> None:
        # Open Data API --> quota
        # "quota_allowed","quota_timespan","quota_used","quota_left","oldest_action_expires_in"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        l_quota = json.loads(lHTTPResponse.read().decode('utf-8'))
        Printer.print("{}/{} requests used in last {} hours".format(
            l_quota['quota_used'],l_quota['quota_allowed'],int(int(l_quota['quota_timespan'])/self.__SECONDS_PER_HOUR)), Level.INFO
        )

    def list_studies(self) -> None:
        l_studies = self.__get_studies()
        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study)

    def quota_exceeded(self) -> bool:
        # Open Data API --> quota
        # "quota_allowed","quota_timespan","quota_used","quota_left","oldest_action_expires_in"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        l_quota = json.loads(lHTTPResponse.read().decode('utf-8'))
        l_downloads_left = int(l_quota['quota_left'])
        Printer.print("{} Rapid7 OpenData API requests left".format(l_downloads_left), Level.INFO)
        return (l_downloads_left == 0)

    def update_studies(self) -> None:
        PROTOCOL = 6
        PORT = 7
        STUDY_UNIQUE_ID = 0
        STUDY_FILENAME = 1
        READ = 'r'

        l_protocols_already_parsed: list = []
        l_interesting_files: list = []

        # if database not built, build database
        self.__initialize_database()

        # save file metadata, mark old files as obsolete and make a list of new files
        l_interesting_files = self.__get_available_sonar_files()
        SQLite.insert_study_file_records(l_interesting_files)
        SQLite.update_obsolete_study_file_records(self.__m_days_until_study_too_old)
        l_usf_records: list = SQLite.get_unparsed_study_file_records()

        # loop through available files but only use newest for any given protocol
        for l_usf_record in l_usf_records:
            l_protocol = "{}_{}".format(l_usf_record[PROTOCOL], l_usf_record[PORT])
            if l_protocol not in l_protocols_already_parsed:
                # if file has new information about a protocol, download the file, parse out the data and delete the file
                l_protocols_already_parsed.append(l_protocol)
                if not self.quota_exceeded():
                    # this stuff needs to go into a method self.__download_study_file()
                    l_study_unique_id: str = l_usf_record[STUDY_UNIQUE_ID]
                    l_study_filename: str = l_usf_record[STUDY_FILENAME]
                    l_local_filename: str = self.__download_study_file(l_study_unique_id, l_study_filename)

                    # this stuff needs to go into method self.__parse_downloaded_study_file
                    # this probably work better with zgrep or pigz
                    # I need to solve the IP range search pattern problem
                    with gzip.open(l_local_filename, READ) as l_file:
                        for l_line in l_file:
                            if ",153.2." in l_line.decode("ASCII"):
                                print('got line', l_line)
                                # parse the record
                                # insert the record

                    SQLite.update_parsed_study_file_record(l_study_filename)
                    self.__delete_study_file(l_local_filename)


                else:
                    raise Exception("Rapid7 Open Data API download quota exceeded. Cannot download file at this time.")

        print(len(l_usf_records))
        print(len(l_protocols_already_parsed))

    # ---------------------------------
    # public static class methods
    # ---------------------------------