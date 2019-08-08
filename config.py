DEBUG = False

DATABASE_FILENAME = "dolphin.sqlite"

RAPID7_OPEN_API_KEY_FILE_PATH = "rapid7-open-api.key"
STUDIES_OF_INTEREST = ['sonar.tcp','sonar.udp']

LOG_ENABLE_LOGGING = True
LOG_FILENAME = "dolphin.log"
LOG_MAX_BYTES_PER_FILE = 1000000
LOG_MAX_NUMBER_LOG_FILES = 3
LOG_LEVEL = 20  #Level: CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0
LOG_FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"