from argparse import RawTextHelpFormatter
from printer import Printer,Level
from argparser import Parser
from sonar import Sonar
import config as Config
import argparse


def run_main_program(pParser: Parser):

    lSonar = Sonar(pParser.verbose, pParser.debug, pParser.rapid7_open_api_key_file_path, pParser.studies_of_interest)
    Printer.verbose = pParser.verbose
    Printer.debug = pParser.debug

    if pParser.show_examples:
        Printer.print_example_usage()

    if pParser.test:
        lSonar.test_connectivity()

    if pParser.quota:
        lSonar.check_quota()

    if pParser.list_studies:
        lSonar.list_studies()

    if pParser.update_studies:
        lSonar.update_studies()

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
    requiredAguments.add_argument('-u', '--update-studies',
                            help='Update database using available Rapid7 Open Data studies and exit',
                            action='store_true')

    run_main_program(pParser=Parser(pArgs=lArgParser.parse_args(), pConfig=Config))