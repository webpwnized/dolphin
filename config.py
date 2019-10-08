DEBUG = False

DATABASE_FILENAME = "dolphin.db"

RAPID7_OPEN_API_KEY_FILE_PATH = "rapid7-open-api.key"
STUDIES_OF_INTEREST = ['sonar.tcp','sonar.udp']
DAYS_UNTIL_STUDY_TOO_OLD = 30

LOG_ENABLE_LOGGING = True
LOG_FILENAME = "dolphin.log"
LOG_MAX_BYTES_PER_FILE = 1000000
LOG_MAX_NUMBER_LOG_FILES = 3
LOG_LEVEL = 30  #Level: CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0
LOG_FORMAT = "%(asctime)s — %(levelname)s — %(message)s"

# Note: Be sure to set up at least one or more of your organization(s) following the example below.
# Index is just integers 1 to N where N is the last record
# Most importantly, make sure the search pattern represents the IP range.
#ORGANIZATIONS = [

#{'index': 1, 'organization_name':'Acme Inc', 'ip_address_range': '15.56.58.0/24', 'search_patterns': ['15.56.58.'], 'additional_notes': 'Roadrunner lives here'},
#{'index': 2, 'organization_name':'Acme Anvils', 'ip_address_range': '12.247.248.2', 'search_patterns': ['12.247.248.2'], 'additional_notes': 'Coyotes office'},
#...MORE RECORDS IF NEEDED...
#{'index': N, 'organization_name':'Acme Logistics', 'ip_address_range': '16.247.248.6', 'search_patterns': ['16.247.248.6'], 'additional_notes': 'Coyote is owner'},
#]

