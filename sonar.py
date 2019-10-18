from printer import Printer, Level
from database import SQLite
from database import StudyFileRecord
from studies import Studies
from datetime import datetime
from argparser import Parser
from enum import Enum
import json
import os
import time
import re
import subprocess
import csv
import hashlib
import getpass
import requests

class Override(Enum):
    FORCE_OUTPUT = True
    USE_DEFAULTS = False

class Sonar:

    # ---------------------------------
    # "Private" class variables
    # ---------------------------------
    __cAPI_KEY_HEADER: str = "X-Api-Key"
    __cUSER_AGENT_HEADER: str = "User-Agent"
    __cUSER_AGENT_VALUE: str = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0"
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
    __m_debug: bool = False
    __m_verbose: bool = False
    __m_api_key_file:str = ""
    __m_studies_of_interest: list = []
    __m_days_until_study_too_old: int = 0
    __mPrinter: Printer = Printer
    __m_organizations: list = []
    __m_export_data: bool = False
    __m_type_of_data_to_export: Studies = None
    __m_export_output_file: str = ""
    __m_use_proxy: bool = False
    __m_proxy_url: str = ""
    __m_proxy_port: int = 0
    __m_proxy_username: str = ""
    __m_proxy_password: str = ""
    __m_open_api_connection_timeout: int = 0
    __m_verify_https_certificate: bool = True
    __m_seconds_to_wait_for_download_credits: float = 600.0

    # ---------------------------------
    # "Public" class variables
    # ---------------------------------

    @property  # getter method
    def export_output_file(self) -> str:
        return self.__m_export_output_file

    @export_output_file.setter  # setter method
    def export_output_file(self: object, p_export_output_file: str):
        self.__m_export_output_file = p_export_output_file

    @property  # getter method
    def type_of_data_to_export(self) -> Studies:
        return self.__m_type_of_data_to_export

    @type_of_data_to_export.setter  # setter method
    def type_of_data_to_export(self: object, p_type_of_data_to_export: Studies):
        self.__m_type_of_data_to_export = p_type_of_data_to_export

    @property  # getter method
    def export_data(self) -> bool:
        return self.__m_export_data

    @export_data.setter  # setter method
    def export_data(self: object, p_export_data: bool):
        self.__m_export_data = p_export_data

    @property  # getter method
    def organizations(self) -> list:
        return self.__m_organizations

    @organizations.setter  # setter method
    def organizations(self: object, p_organizations: list):
        self.__m_organizations = p_organizations

    @property  # getter method
    def verbose(self) -> bool:
        return self.__m_verbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool):
        self.__m_verbose = pVerbose
        self.__mPrinter.verbose = pVerbose

    @property  # getter method
    def debug(self) -> bool:
        return self.__m_debug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool):
        self.__m_debug = pDebug
        self.__mPrinter.debug = pDebug

    @property  # getter method
    def api_key(self) -> str:
        return self.__mAPIKey

    @api_key.setter  # setter method
    def api_key(self: object, pAPIKey: str):
        self.__mAPIKey = pAPIKey

    @property  # getter method
    def api_key_file(self) -> str:
        return self.__m_api_key_file

    @api_key_file.setter  # setter method
    def api_key_file(self: object, pAPIKeyFile: str):
        self.__m_api_key_file = pAPIKeyFile

    @property  # getter method
    def studies_of_interest(self) -> list:
        return self.__m_studies_of_interest

    @studies_of_interest.setter  # setter method
    def studies_of_interest(self: object, pStudiesOfInterest: list):
        self.__m_studies_of_interest = pStudiesOfInterest

    @property  # getter method
    def use_proxy(self) -> bool:
        return self.__m_use_proxy

    @use_proxy.setter  # setter method
    def use_proxy(self: object, p_use_proxy: bool):
        self.__m_use_proxy = p_use_proxy

    @property  # getter method
    def proxy_url(self) -> str:
        return self.__m_proxy_url

    @proxy_url.setter  # setter method
    def proxy_url(self: object, p_proxy_url: str):
        self.__m_proxy_url = p_proxy_url

    @property  # getter method
    def proxy_port(self) -> int:
        return self.__m_proxy_port

    @proxy_port.setter  # setter method
    def proxy_port(self: object, p_proxy_port: int):
        self.__m_proxy_port = p_proxy_port

    @property  # getter method
    def proxy_username(self) -> str:
        return self.__m_proxy_username

    @proxy_username.setter  # setter method
    def proxy_username(self: object, p_proxy_username: str):
        self.__m_proxy_username = p_proxy_username

    @property  # getter method
    def proxy_password(self) -> str:
        return self.__m_proxy_password

    @proxy_password.setter  # setter method
    def proxy_password(self: object, p_proxy_password: str):
        self.__m_proxy_password = p_proxy_password

    @property  # getter method
    def open_api_connection_timeout(self) -> int:
        return self.__m_open_api_connection_timeout

    @open_api_connection_timeout.setter  # setter method
    def open_api_connection_timeout(self: object, p_open_api_connection_timeout: int):
        self.__m_open_api_connection_timeout = p_open_api_connection_timeout

    @property  # getter method
    def verify_https_certificate(self) -> bool:
        return self.__m_verify_https_certificate

    @verify_https_certificate.setter  # setter method
    def verify_https_certificate(self: object, p_verify_https_certificate: bool):
        self.__m_verify_https_certificate = p_verify_https_certificate

    @property  # getter method
    def seconds_to_wait_for_download_credits(self) -> float:
        return self.__m_seconds_to_wait_for_download_credits

    @seconds_to_wait_for_download_credits.setter  # setter method
    def seconds_to_wait_for_download_credits(self: object, p_seconds_to_wait_for_download_credits: float):
        self.__m_seconds_to_wait_for_download_credits = p_seconds_to_wait_for_download_credits

    # ---------------------------------
    # public instance constructor
    # ---------------------------------
    def __init__(self, p_parser: Parser) -> None:
        self.__m_use_proxy = Parser.use_proxy
        self.__m_proxy_url = Parser.proxy_url
        self.__m_proxy_port = Parser.proxy_port
        self.__m_proxy_username = Parser.proxy_username
        self.__m_proxy_password = Parser.proxy_password   
        self.__m_verbose: bool = Parser.verbose
        self.__m_debug: bool = Parser.debug
        self.__mPrinter.verbose = Parser.verbose
        self.__mPrinter.debug = Parser.debug
        self.__m_api_key_file = Parser.rapid7_open_api_key_file_path
        self.__m_studies_of_interest = Parser.studies_of_interest
        self.__m_days_until_study_too_old = Parser.days_until_study_too_old
        self.__m_organizations = Parser.organizations
        self.__m_export_data = True if Parser.export_data else False
        self.__m_type_of_data_to_export = Parser.type_of_data_to_export
        self.__m_export_output_file = Parser.export_output_file
        self.__m_open_api_connection_timeout = Parser.open_api_connection_timeout
        self.__m_verify_https_certificate = Parser.verify_https_certificate
        self.__m_seconds_to_wait_for_download_credits = Parser.seconds_to_wait_for_download_credits
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
        self.__mPrinter.print("Reading Rapid7 Open API key from {}".format(self.api_key_file), Level.INFO)
        with open(self.api_key_file) as lKeyFile:
            self.__mAPIKey = lKeyFile.readline()

    def __connect_to_open_data_api(self, pURL: str):
        self.__mPrinter.print("Connecting to Rapid7 Open API", Level.INFO)

        l_headers = {
            self.__cAPI_KEY_HEADER: self.__mAPIKey,
            self.__cUSER_AGENT_HEADER: self.__cUSER_AGENT_VALUE
        }

        try:
            l_proxies: dict = {}
            if self.__m_use_proxy:
                self.__mPrinter.print("Using upstream proxy", Level.INFO)
                l_proxies = self.__get_proxies()
            lHTTPResponse = requests.get(url=pURL, headers=l_headers, proxies=l_proxies, timeout=self.open_api_connection_timeout, verify=self.__m_verify_https_certificate)
            self.__mPrinter.print("Connected to Rapid7 Open API", Level.SUCCESS)
            return lHTTPResponse
        except Exception as lRequestError:
            self.__mPrinter.print("Cannot connect to Rapid7 Open API: {} {}".format(type(lRequestError).__name__, lRequestError), Level.ERROR)
            exit("Fatal Error: Cannot connect to Rapid7 Open API. Check connectivity to {}. {}".format(
                    self.__cBASE_URL,
                    'Upstream proxy is enabled in config.py. Ensure proxy settings are correct.' if self.__m_use_proxy else 'The proxy is not enabled. Should it be?'))

    def __get_proxies(self):
        # If proxy in use, create proxy URL in the format of http://user:password@example.com:port
        # Otherwise, return empty dictionary
        SCHEME = 0
        BASE_URL = 1
        l_proxy_handler: str = ""
        if not self.__m_proxy_password:
            self.__m_proxy_password = getpass.getpass('Please Enter Proxy Password: ')
        l_parts = self.__m_proxy_url.split('://')
        l_http_proxy_url: str = 'http://{}{}{}@{}{}{}'.format(
            self.__m_proxy_username if self.__m_proxy_username else '',
            ':' if self.__m_proxy_password else '',
            requests.utils.requote_uri(self.__m_proxy_password) if self.__m_proxy_password else '',
            l_parts[BASE_URL],
            ':' if self.__m_proxy_port else '',
            self.__m_proxy_port if self.__m_proxy_port else ''
        )
        l_https_proxy_url = l_http_proxy_url.replace('http://', 'https://')
        l_password_mask = '*' * len(self.__m_proxy_password)
        l_proxy_handlers = {'http':l_http_proxy_url, 'https':l_https_proxy_url}
        self.__mPrinter.print("Building proxy handlers: {},{}".format(
            l_http_proxy_url.replace(self.__m_proxy_password, l_password_mask),
            l_https_proxy_url.replace(self.__m_proxy_password, l_password_mask)), Level.INFO)
        return l_proxy_handlers

    def __get_studies(self) -> list:
        # Open Data API --> studies
        # "uniqid","name","short_desc","long_desc","study_url","study_name","study_venue",
        # "study_bibtext","contact_name","contact_email","organization_name","organization_website",
        # "created_at","updated_at","sonarfile_set"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cSTUDIES_URL)
        return (json.loads(lHTTPResponse.text))

    def __study_is_interesting(self, p_study: dict) -> bool:
        return(p_study['uniqid'] in self.studies_of_interest)

    def __print_study_metadata(self, pStudy: dict, p_force_output: Override) -> None:
        # Open Data API --> studies
        # "uniqid","name","short_desc","long_desc","study_url","study_name","study_venue",
        # "study_bibtext","contact_name","contact_email","organization_name","organization_website",
        # "created_at","updated_at","sonarfile_set"
        p_debug_level = Level.PRINT_REGARDLESS if p_force_output.FORCE_OUTPUT else Level.INFO
        self.__mPrinter.print("Found study of interest", Level.SUCCESS)
        self.__mPrinter.print("{} {}".format(pStudy['uniqid'], pStudy['name']), p_debug_level)
        self.__mPrinter.print("Updated: {}".format(pStudy['updated_at']), p_debug_level)
        self.__mPrinter.print("{}".format(pStudy['short_desc']), p_debug_level)
        self.__mPrinter.print("{}".format(pStudy['long_desc']), p_debug_level)
        self.__mPrinter.print("{} files are available".format(len(pStudy['sonarfile_set'])), p_debug_level)

    def __print_study_filename_record(self, l_record: StudyFileRecord) -> None:
        print()
        self.__mPrinter.print("Filename: {}, Protocol: {}, Port:{}, Timestamp: {}".format(l_record.filename,l_record.protocol,l_record.port,l_record.timestamp_string), Level.INFO)

    def __parse_study_filename(self, p_study: str, p_filename: str) -> StudyFileRecord:

        l_record = StudyFileRecord()
        l_parts = p_filename.split('.')[0].split('-')

        try:
            l_record.study_uniqid = p_study
            l_record.filename = p_filename
            l_record.year = int(l_parts[self.__cYEAR])
            l_record.month = int(l_parts[self.__cMONTH])
            l_record.day = int(l_parts[self.__cDAY])
            l_record.timestamp = int(l_parts[self.__cEPOCH_TIME])
            l_record.timestamp_string = datetime.fromtimestamp((float(l_parts[self.__cEPOCH_TIME])))

            l_protocol_port = l_parts[self.__cFILESET].rsplit('_', self.__cLAST_OCCURENCE)
            if l_protocol_port.__len__() == 2 and str.isdigit(l_protocol_port[1]):
                l_record.protocol = l_protocol_port[0]
                l_record.port = int(l_protocol_port[1])
            elif l_protocol_port.__len__() == 2:
                l_record.protocol = "".format(l_protocol_port[0], l_protocol_port[1])
                l_record.port = -1
            elif l_protocol_port.__len__() == 1:
                l_record.protocol = l_protocol_port[0]
                l_record.port = -1
            else:
                self.__mPrinter.print("Unexpected format: {}".format(l_protocol_port), Level.WARNING)

            self.__print_study_filename_record(l_record)
            return l_record
        except IndexError as l_index_error:
            l_record = None
            self.__mPrinter.print("Unexpected format: {} {} {}".format(l_index_error, p_filename, l_parts), Level.WARNING)

    def __parse_protocol_line(self, p_study_file_line: str, p_organization: dict, p_study_file_record: list) -> tuple:
        # Discovered Service
        # "ipv4_address,"
        # "port,"
        # "protocol,"
        # "study_uniqid,"
        # "filename,"
        # "organization_name TEXT,"
        # "ip_address_range TEXT,"
        # "additional_notes TEXT,"
        # "discovered_timestamp,"
        # "discovered_timestamp_string,"
        # "parsed_timestamp,"
        # "parsed_timestamp_string"

        STUDY_FILE_LINE_TIMESTAMP_TS = 0
        STUDY_FILE_LINE_SADDR = 1
        STUDY_FILE_LINE_SPORT = 2

        STUDY_FILE_RECORD_STUDY_UNIQUE_ID = 0
        STUDY_FILE_RECORD_STUDY_FILENAME = 1
        STUDY_FILE_RECORD_PROTOCOL = 6

        l_now: int = int(time.mktime(time.localtime()))
        l_fields: list = p_study_file_line.split(",")
        l_record: tuple = (l_fields[STUDY_FILE_LINE_SADDR], l_fields[STUDY_FILE_LINE_SPORT],
                           p_study_file_record[STUDY_FILE_RECORD_PROTOCOL], p_study_file_record[STUDY_FILE_RECORD_STUDY_UNIQUE_ID],
                           p_study_file_record[STUDY_FILE_RECORD_STUDY_FILENAME], p_organization["organization_name"],
                           p_organization["ip_address_range"], p_organization["additional_notes"],
                           l_fields[STUDY_FILE_LINE_TIMESTAMP_TS], l_fields[STUDY_FILE_LINE_TIMESTAMP_TS], l_now, l_now)

        return l_record

    def __format_file_size(self, p_file_size_bytes: int, p_suffix: str = 'B'):
        l_file_size: str = ""
        for l_unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(p_file_size_bytes) < 1024.0:
                return "{} {}{}".format(round(p_file_size_bytes,2), l_unit, p_suffix)
            p_file_size_bytes /= 1024.0

    def __get_study_file_information(self, p_study: str, p_filname: str) -> dict:
        # Open Data API --> studies/<study unique ID>/<filename>
        # "name", "fingerprint", "size (bytes)", "updated_at"
        self.__mPrinter.print("Fetching metadata: study {}, file {}".format(p_study, p_filname), Level.INFO)
        l_file_metadata_url: str = "{}{}/{}/".format(self.__cFILE_METADATA_BASE_URL, p_study, p_filname)
        lHTTPResponse = self.__connect_to_open_data_api(l_file_metadata_url)
        l_file_metadata: dict = json.loads(lHTTPResponse.text)
        self.__mPrinter.print("File {}: fingerprint {}, {}, updated at {}".format(l_file_metadata["name"],l_file_metadata["fingerprint"],self.__format_file_size(int(l_file_metadata["size"])),l_file_metadata["updated_at"]), Level.INFO)
        return l_file_metadata

    def __get_study_file_download_link(self, p_study: str, p_filname: str) -> str:
        # Open Data API --> studies/<study unique ID>/<filename>/download/
        # "url"
        self.__mPrinter.print("Fetching study file download link: study {}, file {}".format(p_study, p_filname), Level.INFO)
        l_download_url: str = "{}{}/{}/download/".format(self.__cFILE_DOWNLOAD_BASE_URL, p_study, p_filname)
        lHTTPResponse = self.__connect_to_open_data_api(l_download_url)
        l_response: dict = json.loads(lHTTPResponse.text)
        l_download_link: str = l_response['url']
        self.__mPrinter.print("Fetched download link for file {} from study {}: {}".format(p_filname, p_study, l_download_link), Level.SUCCESS)
        return l_download_link

    def __study_file_record_is_new(self, p_study_file_record: StudyFileRecord) -> bool:
        l_newer_record_already_in_database: bool = bool(SQLite.get_newer_study_file_records(p_study_file_record.port, p_study_file_record.protocol, p_study_file_record.timestamp).__len__())
        return not l_newer_record_already_in_database

    def __get_available_sonar_files(self) -> list:
        l_studies: list = self.__get_studies()
        l_interesting_files = []

        self.__mPrinter.print("Checking if any interesting Sonar files are available for download", Level.INFO)

        # if an interesting file is found in an interesting study, download the file metadata
        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study, Override.USE_DEFAULTS)
                for l_filename in l_study['sonarfile_set']:
                    l_sf_record: StudyFileRecord = self.__parse_study_filename(l_study['uniqid'], l_filename)
                    if l_sf_record:
                        if self.__study_file_record_is_new(l_sf_record):
                            l_interesting_files.append((l_sf_record.study_uniqid, l_sf_record.filename, l_sf_record.year, l_sf_record.month, l_sf_record.day, l_sf_record.timestamp, l_sf_record.timestamp_string, l_sf_record.protocol, l_sf_record.port))

        return l_interesting_files

    def __verify_downloaded_file(self, p_local_filename: str, p_fingerprint: str) -> bool:
        BLOCKSIZE = 65536
        READ_BYTES = 'rb'

        self.__mPrinter.print("Verifying hash of downloaded study file {}".format(p_local_filename), Level.INFO)

        l_hash_generator = hashlib.sha1()
        with open(p_local_filename, READ_BYTES) as l_file:
            buf = l_file.read(BLOCKSIZE)
            while len(buf) > 0:
                l_hash_generator.update(buf)
                buf = l_file.read(BLOCKSIZE)
        return l_hash_generator.hexdigest() == p_fingerprint

    def __download_study_file(self, p_study, p_filename) -> str:
        WRITE_BYTES: str = 'wb'

        self.__mPrinter.print("Downloading interesting study file: study {}, file {}".format(p_study, p_filename), Level.INFO)

        #TODO: Use this information to enrich the study file records
        l_file_information: dict = self.__get_study_file_information(p_study, p_filename)
        l_download_link: str = self.__get_study_file_download_link(p_study, p_filename)
        l_local_filename: str = "/tmp/{}".format(p_filename)
        l_proxies: dict = {}

        self.__mPrinter.print("Beginning download", Level.INFO)
        if self.__m_use_proxy:
            self.__mPrinter.print("Using upstream proxy", Level.INFO)
            l_proxies = self.__get_proxies()
        l_http_response = requests.get(l_download_link, proxies=l_proxies, verify=self.__m_verify_https_certificate)
        open(l_local_filename, WRITE_BYTES).write(l_http_response.content)
        self.__mPrinter.print("Downloaded file to {}".format(l_local_filename), Level.SUCCESS)

        if self.__verify_downloaded_file(l_local_filename, l_file_information['fingerprint']):
            self.__mPrinter.print("Downloaded file passed hash verification",
                          Level.SUCCESS)
        else:
            self.__mPrinter.print("Downloaded file failed hash verification: {}".format(p_filename),
                          Level.ERROR)

        return l_local_filename

    def __delete_study_file(self, p_local_filename: str) -> None:
        try:
            self.__mPrinter.print("Deleting file to {}".format(p_local_filename), Level.SUCCESS)
            os.remove(p_local_filename)
        except OSError:
            pass

    def __index_search_patterns(self) -> dict:
        # In this space for time trade-off, organization records are indexed by search pattern
        # In the organizations dictionary, organizations are indexed by "index". In this new
        # dictionary "l_indexed_search_patterns", the index is the search pattern and the
        # value is the "index" field from the organizations dictionary. If a match is found
        # on a search pattern, it will be easy to retrieve the meta-data about the organization.
        self.__mPrinter.print("Indexing search patterns", Level.INFO)
        l_indexed_search_patterns: dict = {}
        l_regexp = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        for l_organization in self.__m_organizations:
            for l_search_pattern in l_organization['search_patterns']:
                #The comma is added before the search pattern because the records from Rapid7 are CSV format
                # i.e. to search for 10.20.30.0/24 we need to search for and record with ",10.20.30"
                # To search for full ip like 10.10.10.10, be sure to add the training comma i.e. ",10.10.10.10,"
                l_trailing_comma = ',' if re.match(l_regexp, l_search_pattern) else ''
                l_indexed_search_patterns.update({'{}{}{}'.format(',', l_search_pattern, l_trailing_comma): l_organization['index']})

        return l_indexed_search_patterns

    def __sleep_until_download_credits_available(self):
        self.__mPrinter.print("Checking quota", Level.INFO)
        while self.quota_exceeded():
            self.__mPrinter.print("Quota exceeded. The current time is {}. I will try again in {} minutes".format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.__m_seconds_to_wait_for_download_credits / 60), Level.WARNING)
            time.sleep(self.__m_seconds_to_wait_for_download_credits)
        self.__mPrinter.print("We have download credits. Proceeding with update.", Level.SUCCESS)

    # ---------------------------------
    # public instance methods
    # ---------------------------------
    def test_connectivity(self) -> None:
        try:
            lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
            if not self.verbose:
                self.__mPrinter.print("SUCCESS: Connected to Rapid7 Open Data API", Level.PRINT_REGARDLESS)
        except:
            self.__mPrinter.print("Connection test failed. Unable to connect to Rapid7 Open Data API", Level.ERROR)

    def check_quota(self) -> None:
        # Open Data API --> quota
        # "quota_allowed","quota_timespan","quota_used","quota_left","oldest_action_expires_in"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        l_quota = json.loads(lHTTPResponse.text)
        self.__mPrinter.print("{}/{} requests used in last {} hours. {} downloads remaining.".format(
            l_quota['quota_used'],l_quota['quota_allowed'],int(int(l_quota['quota_timespan'])/self.__SECONDS_PER_HOUR), int(l_quota['quota_allowed']) - int(l_quota['quota_used'])), Level.PRINT_REGARDLESS
        )

    def list_studies(self) -> None:
        l_studies = self.__get_studies()
        for l_study in l_studies:
            if self.__study_is_interesting(l_study):
                self.__print_study_metadata(l_study, Override.FORCE_OUTPUT)

    def list_unparsed_files(self) -> None:
        study_uniqid = 0
        filename = 1
        year = 2
        month = 3
        day = 4
        timestamp = 5
        protocol = 6
        port = 7
        l_usf_records: list = SQLite.get_unparsed_study_file_records()
        for l_record in l_usf_records:
            self.__mPrinter.print("{}\t{}\t{}\t{}-{}-{}".format(l_record[0],l_record[6],l_record[7],l_record[2],l_record[3],l_record[4],), Level.PRINT_REGARDLESS)

    def quota_exceeded(self) -> bool:
        # Open Data API --> quota
        # "quota_allowed","quota_timespan","quota_used","quota_left","oldest_action_expires_in"
        lHTTPResponse = self.__connect_to_open_data_api(self.__cQUOTA_URL)
        l_quota = json.loads(lHTTPResponse.text)
        l_downloads_left = int(l_quota['quota_left'])
        self.__mPrinter.print("{} Rapid7 OpenData API requests left".format(l_downloads_left), Level.INFO)
        return (l_downloads_left == 0)

    def update_studies(self) -> None:
        PROTOCOL = 6
        PORT = 7
        STUDY_UNIQUE_ID = 0
        STUDY_FILENAME = 1
        READ = 'r'
        APPEND = 'a'

        l_protocols_already_parsed: list = []
        l_discovered_service_records: list = []

        self.__mPrinter.print("Fetching and parsing unparsed study files in search of network services", Level.INFO)

        # if database not built, build database
        # TODO: Normalize database tables
        self.__initialize_database()

        # re-organize the search patterns into a dictionary
        # TODO: Convert search patterns to regular expressions
        l_indexed_search_patterns: dict = self.__index_search_patterns()

        # save file metadata, mark old files as obsolete and fetch a list of new files
        l_interesting_files: list = self.__get_available_sonar_files()
        SQLite.insert_new_study_file_records(l_interesting_files)
        SQLite.update_obsolete_study_file_records(self.__m_days_until_study_too_old)
        l_usf_records: list = SQLite.get_unparsed_study_file_records()

        # loop through available files but only use newest for any given protocol
        for l_usf_record in l_usf_records:

            self.__sleep_until_download_credits_available()

            l_study_filename: str = l_usf_record[STUDY_FILENAME]
            l_protocol: str = l_usf_record[PROTOCOL]
            l_port: int =  l_usf_record[PORT]
            l_protocol_id: str = "{}_{}".format(l_protocol, l_port)

            self.__mPrinter.print("Parsing study {}".format(l_study_filename), Level.INFO)

            if l_protocol_id in l_protocols_already_parsed:
                SQLite.update_outdated_study_file_record(l_study_filename)
            else:
                # if file has new information about a protocol, download the file, parse out the data and delete the file
                l_protocols_already_parsed.append(l_protocol_id)
                l_study_unique_id: str = l_usf_record[STUDY_UNIQUE_ID]
                l_local_filename: str = self.__download_study_file(l_study_unique_id, l_study_filename)

                if l_study_unique_id == Studies.SONAR_TCP.value or l_study_unique_id == Studies.SONAR_UDP.value:

                    # TODO: this stuff needs to go into method self.__parse_downloaded_study_file
                    l_temp_filename = "/tmp/records"
                    if os.path.exists(l_temp_filename):
                        os.remove(l_temp_filename)
                    subprocess.call(["touch", l_temp_filename])
                    l_output_file = open(l_temp_filename, APPEND)
                    l_number_patterns = len(l_indexed_search_patterns)
                    self.__mPrinter.print("Placing search results into temp file {}".format(l_temp_filename), Level.INFO)
                    for l_index, l_search_pattern in enumerate(l_indexed_search_patterns, start=1):
                        self.__mPrinter.print("Searching pattern {} - {} of {} ({:0.2f}%) in {}".format(l_search_pattern, l_index, l_number_patterns, l_index/l_number_patterns*100, l_local_filename), Level.INFO)
                        subprocess.call(["zgrep", "-F", l_search_pattern,l_local_filename], stdout=l_output_file)
                        l_output_file.flush()
                    l_output_file.close()

                    with open(l_temp_filename, READ) as l_temp_file:
                        for l_line in l_temp_file:
                            for l_search_pattern in l_indexed_search_patterns:
                                if l_search_pattern in l_line:
                                    l_discovered_service_record: tuple = self.__parse_protocol_line(l_line,
                                                                    self.__m_organizations[l_indexed_search_patterns[l_search_pattern]],
                                                                    l_usf_record)
                                    l_discovered_service_records.append(l_discovered_service_record)
                                    self.__mPrinter.print("Service discovered: {}".format(l_discovered_service_record), Level.INFO)

                    SQLite.delete_obsolete_service_records(l_port, l_protocol)
                    if l_discovered_service_records:
                        SQLite.insert_discovered_service_records(l_discovered_service_records)
                    else:
                        self.__mPrinter.print("No {} services discovered in {}".format(l_study_unique_id, l_study_filename), Level.WARNING)
                    SQLite.update_parsed_study_file_record(l_study_filename)
                    self.__delete_study_file(l_local_filename)

                else:
                    raise Exception("Rapid7 Open Data API download quota exceeded. Cannot download file at this time. Dont worry. I keep track. Ill get them next time.")

    def export_dataset(self) -> None:
        WRITE = 'w'

        l_column_names: list = SQLite.get_table_column_names('discovered_services')
        l_ds_records: list = SQLite.get_discovered_service_records(self.type_of_data_to_export)
        with open(self.export_output_file, WRITE) as l_file:
            l_csv_writer = csv.writer(l_file, csv.excel)
            l_csv_writer.writerow(l_column_names)
            l_csv_writer.writerows(l_ds_records)