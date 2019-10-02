import config as Config
from studies import Studies

class Parser:

    debug: bool = False
    verbose: bool = False
    test_connectivity: bool = False
    check_quota: bool = False
    show_examples: bool = False
    list_studies: bool = False
    update_studies: bool = False
    rapid7_open_api_key_file_path: str = ""
    studies_of_interest: list = []
    days_until_study_too_old: int = 0
    database_filename: str = ""
    enable_logging: bool = False
    log_filename: str = ""
    log_max_bytes_per_file: int = 0
    log_max_number_log_files: int = 0
    log_level: int = 0
    log_format: str = ""
    organizations: list = []
    export_data: bool = False
    type_of_data_to_export: str = ""
    export_output_file: str = ""

    # static methods
    @staticmethod
    def parse_configuration(p_args, p_config: Config) -> None:
        Parser.verbose = p_args.verbose
        Parser.test_connectivity = p_args.test
        Parser.check_quota = p_args.quota
        Parser.debug = (p_args.debug if p_args.debug else p_config.DEBUG)
        Parser.show_examples = p_args.examples
        Parser.list_studies = p_args.list_studies
        Parser.update_studies = p_args.update_studies
        if p_args.export_data:
            Parser.export_data = True
            Parser.export_output_file = p_args.output_file
            if p_args.export_data == 'TCP':
                Parser.type_of_data_to_export = Studies.SONAR_TCP
            elif p_args.export_data == 'UDP':
                Parser.type_of_data_to_export = Studies.SONAR_UDP
        Parser.rapid7_open_api_key_file_path = p_config.RAPID7_OPEN_API_KEY_FILE_PATH
        Parser.studies_of_interest = p_config.STUDIES_OF_INTEREST
        Parser.database_filename = p_config.DATABASE_FILENAME
        Parser.enable_logging = p_config.LOG_ENABLE_LOGGING
        Parser.log_filename = p_config.LOG_FILENAME
        Parser.log_max_bytes_per_file = p_config.LOG_MAX_BYTES_PER_FILE
        Parser.log_max_number_log_files = p_config.LOG_MAX_NUMBER_LOG_FILES
        Parser.log_level = p_config.LOG_LEVEL
        Parser.log_format = p_config.LOG_FORMAT
        Parser.days_until_study_too_old = p_config.DAYS_UNTIL_STUDY_TOO_OLD
        Parser.organizations = p_config.ORGANIZATIONS

