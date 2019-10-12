## Project Announcements

* Twitter: [https://twitter.com/webpwnized](https://twitter.com/webpwnized)
* YouTube: [https://www.youtube.com/user/webpwnized](https://www.youtube.com/user/webpwnized)

## Usage

    dolphin.py [-h] [-v] [-d] (-e | -t | -q | -l | -p | -u | -x EXPORT_DATA) [-o OUTPUT_FILE]
        
### Optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Enable verbose output such as current progress and duration
      -d, --debug           Enable debug mode
      -e, --examples        Show examples and exit
      -t, --test            Test connectivity to Rapid7 Open Data API and exit
      -q, --quota           Display Rapid7 Open Data API quota and exit
      -l, --list-studies    List available Rapid7 Open Data studies and exit
      -p, --list-unparsed   List unparsed Rapid7 Open Data study files and exit. Dolphin knows about these files but has not downloaded and parsed the files yet.
      -u, --update-studies  Update database using available Rapid7 Open Data studies and exit. Uses proxy settings in config file if set. Check quota before calling.
      -x EXPORT_DATA, --export-data EXPORT_DATA
                            Export data as CSV file to <output_file>. Must provide as one of ['SONAR_TCP', 'SONAR_UDP'].
      -o OUTPUT_FILE, --output-file OUTPUT_FILE
                            Output file into which exported data is saved. Required if -x, --export-data provided

## Examples

#### Test connectivity to Rapid7 Open Data API

        python3 dolphin.py --verbose --test
        python3 byepass.py -v -t
    
#### Display Rapid7 Open Data API quota
    
        python3 dolphin.py --verbose --quota
        python3 byepass.py -v -q
    
#### List available Rapid7 Open Data studies
    
        python3 dolphin.py --verbose --list-studies
        python3 byepass.py -v -l
    
#### List un-parsed Rapid7 Open Data studies
    
        python3 dolphin.py --verbose --list-unparsed
        python3 byepass.py -v -p
    
#### Update database using available Rapid7 Open Data studies
    
        python3 dolphin.py --verbose --update-studies
        python3 byepass.py -v -u
    
#### Update database using available Rapid7 Open Data studies
    
        python3 dolphin.py --verbose --export-data SONAR_TCP --output-file /tmp/data.csv
        python3 byepass.py -v -x SONAR_TCP -o /tmp/data.csv
    
        python3 dolphin.py --verbose --export-data SONAR_UDP --output-file /tmp/data.csv
        python3 byepass.py -v -x SONAR_UDP -o /tmp/data.csv

## Dependencies

* [Python3](https://www.python.org/)
* [requests](https://pypi.org/project/requests/)

## References

* [Rapid7 Open Data Documentation](https://opendata.rapid7.com/about/)
* [Rapid7 Open Data API Documentation](https://opendata.rapid7.com/apihelp/)
