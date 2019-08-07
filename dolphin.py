from argparse import RawTextHelpFormatter
from printer import Printer,Level
from argparser import Parser
from sonar import Sonar
import config as Config
import argparse


def run_main_program():

    if Parser.show_examples:
        Printer.print_example_usage()
        exit(0)

    lSonar = Sonar(p_parser=Parser)
    Printer.verbose = Parser.verbose
    Printer.debug = Parser.debug

    if Parser.test_connectivity:
        lSonar.test_connectivity()

    if Parser.check_quota:
        lSonar.check_quota()

    if Parser.list_studies:
        lSonar.list_studies()

    if Parser.update_studies:
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

    Parser.parse_configuration(p_args=lArgParser.parse_args(), p_config=Config)
    run_main_program()