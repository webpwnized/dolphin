from argparse import RawTextHelpFormatter
from printer import Printer,Level
from argparser import Parser
from sonar import Sonar
from studies import Studies
import config as Config
import argparse
import sys

def run_main_program():

    Printer.verbose = Parser.verbose
    Printer.debug = Parser.debug
    Printer.log_filename = Parser.log_filename
    Printer.log_level = Parser.log_level
    Printer.log_max_bytes_per_file = Parser.log_max_bytes_per_file
    Printer.log_max_number_log_files = Parser.log_max_number_log_files
    Printer.log_format = Parser.log_format
    Printer.enable_logging()

    if Parser.show_examples:
        Printer.print_example_usage()
        exit(0)

    lSonar = Sonar(p_parser=Parser)

    if Parser.test_connectivity:
        lSonar.test_connectivity()

    if Parser.check_quota:
        lSonar.check_quota()

    if Parser.list_studies:
        lSonar.list_studies()

    if Parser.list_unparsed_files:
        lSonar.list_unparsed_files()

    if Parser.update_studies:
        lSonar.update_studies()

    if Parser.export_data:
        lSonar.export_dataset()

if __name__ == '__main__':

    lArgParser = argparse.ArgumentParser(description="""
  ____        _       _     _  
 |  _ \  ___ | |_ __ | |__ (_)_ __  
 | | | |/ _ \| | '_ \| '_ \| | '_ \ 
 | |_| | (_) | | |_) | | | | | | | |
 |____/ \___/|_| .__/|_| |_|_|_| |_|
               |_|                  
 
 Automated Sonar file analysis - Fortuna Fortis Paratus
""", formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-v', '--verbose',
                            help='Enable verbose output such as current progress and duration',
                            action='store_true')
    lArgParser.add_argument('-d', '--debug',
                            help='Enable debug mode',
                            action='store_true')
    requiredAguments = lArgParser.add_mutually_exclusive_group(required=True)
    requiredAguments.add_argument('-e', '--examples',
                            help='Show examples and exit',
                            action='store_true')
    requiredAguments.add_argument('-t', '--test',
                            help='Test connectivity to Rapid7 Open Data API and exit',
                            action='store_true')
    requiredAguments.add_argument('-q', '--quota',
                            help='Display Rapid7 Open Data API quota and exit',
                            action='store_true')
    requiredAguments.add_argument('-l', '--list-studies',
                            help='List available Rapid7 Open Data studies and exit',
                            action='store_true')
    requiredAguments.add_argument('-p', '--list-unparsed',
                            help='List unparsed Rapid7 Open Data study files and exit. Dolphin knows about these files but has not downloaded and parsed the files yet.',
                            action='store_true')
    requiredAguments.add_argument('-u', '--update-studies',
                            help='Update database using available Rapid7 Open Data studies and exit. Uses proxy settings in config file if set.',
                            action='store_true')
    requiredAguments.add_argument('-x', '--export-data',
                            help='Export data as CSV file to <output_file>. Must provide as one of {}.'.format([Study.name for Study in Studies]),
                            action='store')
    lArgParser.add_argument('-o', '--output-file',
                            help='Output file into which exported data is saved. Required if -x, --export-data provided',
                            required=('-x' in sys.argv or '--export-data' in sys.argv)) #only required if --export-data is given

    Parser.parse_configuration(p_args=lArgParser.parse_args(), p_config=Config)
    run_main_program()