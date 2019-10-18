import sqlite3
from printer import Printer, Level
from urllib.request import pathname2url
from enum import Enum
import time
from studies import Studies

class StudyFileRecord():
    study_uniqid: str = ""
    filename: str = ""
    year: int = 0
    month: int = 0
    day: int = 0
    timestamp: int = 0
    timestamp_string: str = ""
    protocol: str = ""
    port: int = 0

class Mode(Enum):
    READ_ONLY = 'ro'
    READ_WRITE = 'rw'
    READ_WRITE_CREATE = 'rwc'
    IN_MEMORY = 'memory'

class SQLite():

    ATTACHED_DATABASE_FILENAME: int = 2
    SECONDS_PER_DAY = 24 * 60 * 60

    database_filename: str = ""

    @staticmethod
    def __connect_to_database(p_mode: Mode) -> sqlite3.Connection:
        FIRST_ROW = 0
        try:
            l_database_file_uri: str = 'file:{}?mode={}'.format(pathname2url(SQLite.database_filename), p_mode.value)
            l_connection: sqlite3.Connection = sqlite3.connect(l_database_file_uri, uri=True)
            Printer.print("Connected to SQLite version {} database".format(sqlite3.sqlite_version), Level.SUCCESS)
            l_query:str = "SELECT * FROM pragma_database_list();"
            l_rows = SQLite.__execute_query(l_connection, l_query)
            Printer.print("Attached database: {}".format(l_rows[FIRST_ROW][SQLite.ATTACHED_DATABASE_FILENAME]), Level.INFO)
            return l_connection
        except sqlite3.OperationalError as l_error:
            Printer.print("Error connecting to database: {}".format(l_error), Level.ERROR)
            return None
        except Exception as l_error:
            Printer.print("Error connecting to database: {} {}".format(type(l_error).__name__, l_error), Level.ERROR)
            return None

    @staticmethod
    def __print_rows_affected(p_cursor: sqlite3.Cursor, p_query: str) -> None:
        FIRST_ROW = 0
        FIRST_COLUMN = 0
        if "SELECT" not in p_query:
            p_cursor.execute("SELECT changes();")
            l_changes: list = p_cursor.fetchall()
            Printer.print("Rows affected: {}".format(l_changes[FIRST_ROW][FIRST_COLUMN]), Level.INFO)

    @staticmethod
    def __execute_query(p_connection: sqlite3.Connection, p_query: str) -> list:
        try:
            l_cursor: sqlite3.Cursor = p_connection.cursor()
            l_cursor.execute(p_query)
            l_rows: list = l_cursor.fetchall()
            p_connection.commit()
            Printer.print("Executed SQLite query: {}".format(p_query), Level.DEBUG)
            SQLite.__print_rows_affected(l_cursor, p_query)
            return l_rows
        except sqlite3.ProgrammingError as l_error:
            Printer.print("Programming Error: executing SQLite query: {}".format(l_error), Level.ERROR)
        except sqlite3.OperationalError as l_error:
            Printer.print("Operational Error executing SQLite query: {}".format(l_error), Level.ERROR)

    @staticmethod
    def __execute_parameterized_query(p_connection: sqlite3.Connection, p_query: str, p_parameters: tuple) -> list:
        try:
            l_cursor: sqlite3.Cursor = p_connection.cursor()
            l_cursor.execute(p_query, p_parameters)
            l_rows: list = l_cursor.fetchall()
            p_connection.commit()
            Printer.print("Executed SQLite query: {}".format(p_query), Level.DEBUG)
            SQLite.__print_rows_affected(l_cursor, p_query)
            return l_rows
        except sqlite3.ProgrammingError as l_error:
            Printer.print("Programming Error: executing SQLite query: {}".format(l_error), Level.ERROR)
        except sqlite3.OperationalError as l_error:
            Printer.print("Operational Error executing SQLite query: {}".format(l_error), Level.ERROR)

    @staticmethod
    def __execute_parameterized_queries(p_connection: sqlite3.Connection, p_query: str, p_records: list) -> list:
        try:
            l_cursor: sqlite3.Cursor = p_connection.cursor()
            l_cursor.executemany(p_query, p_records)
            l_rows: list = l_cursor.fetchall()
            p_connection.commit()
            Printer.print("Executed SQLite query: {}".format(p_query), Level.DEBUG)
            SQLite.__print_rows_affected(l_cursor, p_query)
            return l_rows
        except sqlite3.ProgrammingError as l_error:
            Printer.print("Programming Error: executing SQLite query: {}".format(l_error), Level.ERROR)
        except sqlite3.OperationalError as l_error:
            Printer.print("Operational Error executing SQLite query: {}".format(l_error), Level.ERROR)

    @staticmethod
    def __verify_table_exists(p_connection: sqlite3.Connection, p_table_name: str) -> bool:
        l_query: str = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(p_table_name)
        l_rows: list = SQLite.__execute_query(p_connection, l_query)
        if not l_rows:
            Printer.print("Table {} not found in database".format(p_table_name), Level.ERROR)
        return bool(l_rows)

    @staticmethod
    def __enable_foreign_keys(p_connection: sqlite3.Connection) -> None:
        l_query: str = "PRAGMA foreign_keys = 1;"
        Printer.print("Enabling foreign keys", Level.INFO)
        SQLite.__execute_query(p_connection, l_query)
        Printer.print("Enabled foreign keys", Level.SUCCESS)

    @staticmethod
    def verify_database_exists() -> bool:
        l_connection:sqlite3.Connection = None
        try:
            Printer.print("Checking if database is available", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            if l_connection:
                return SQLite.__verify_table_exists(l_connection, "study_files")
            else:
                return False
        except sqlite3.Error as l_error:
            Printer.print("Error connecting to database: {}".format(l_error), Level.WARNING)
            return False
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def __create_parse_status_table(p_connection: sqlite3.Connection) -> None:
        l_query: str = "CREATE TABLE IF NOT EXISTS main.parse_status(" \
                       "parsed TEXT NOT NULL PRIMARY KEY," \
                       "parsed_description TEXT NOT NULL" \
                       ");"
        Printer.print("Creating table parse_status", Level.INFO)
        SQLite.__execute_query(p_connection, l_query)

        l_query: str = "INSERT OR IGNORE INTO main.parse_status(" \
                       "parsed," \
                       "parsed_description" \
                       ") VALUES ('N', 'Not parsed');"
        SQLite.__execute_query(p_connection, l_query)

        l_query: str = "INSERT OR IGNORE INTO main.parse_status(" \
                       "parsed," \
                       "parsed_description" \
                       ") VALUES ('Y', 'Parsed');"
        SQLite.__execute_query(p_connection, l_query)

        l_query: str = "INSERT OR IGNORE INTO main.parse_status(" \
                       "parsed," \
                       "parsed_description" \
                       ") VALUES ('I', 'In progress');"
        SQLite.__execute_query(p_connection, l_query)

        l_query: str = "INSERT OR IGNORE INTO main.parse_status(" \
                       "parsed," \
                       "parsed_description" \
                       ") VALUES ('O', 'Outdated file');"
        SQLite.__execute_query(p_connection, l_query)

        Printer.print("Created table parse_status", Level.SUCCESS)

    @staticmethod
    def __create_study_files_table(p_connection: sqlite3.Connection) -> None:

        l_query: str = "CREATE TABLE IF NOT EXISTS main.study_files(" \
                           "study_uniqid TEXT," \
                           "filename TEXT PRIMARY KEY," \
                           "year INTEGER," \
                           "month INTEGER," \
                           "day INTEGER," \
                           "timestamp INTEGER," \
                           "timestamp_string TEXT," \
                           "protocol TEXT," \
                           "port INTEGER," \
                           "parsed TEXT DEFAULT 'N' NOT NULL," \
                           "parsed_timestamp INTEGER," \
                           "parsed_timestamp_string TEXT," \
                           "FOREIGN KEY(parsed) REFERENCES parse_status(parsed)" \
                       ");"
        Printer.print("Creating table study_files", Level.INFO)
        SQLite.__execute_query(p_connection, l_query)
        Printer.print("Created table study_files", Level.SUCCESS)

    @staticmethod
    def __create_discovered_services_table(p_connection: sqlite3.Connection) -> None:

        l_query: str = "CREATE TABLE IF NOT EXISTS main.discovered_services(" \
                            "ipv4_address TEXT," \
                            "port INTEGER," \
                            "protocol TEXT," \
                            "study_uniqid TEXT," \
                            "filename TEXT," \
                            "organization_name TEXT," \
                            "ip_address_range TEXT," \
                            "additional_notes TEXT," \
                            "discovered_timestamp INTEGER," \
                            "discovered_timestamp_string TEXT," \
                            "parsed_timestamp INTEGER," \
                            "parsed_timestamp_string TEXT," \
                            "PRIMARY KEY(ipv4_address, port)" \
                       ");"

        Printer.print("Creating table discovered_services", Level.INFO)
        SQLite.__execute_query(p_connection, l_query)
        Printer.print("Created table discovered_services", Level.SUCCESS)

    @staticmethod
    def get_table_column_names(p_table_name: str) -> list:
        NAME = 1
        try:
            Printer.print("Fetching column names for table {}".format(p_table_name), Level.INFO)
            l_column_names: list = SQLite.get_table_column_metadata(p_table_name)
            l_names = []
            for l_column_tuple in l_column_names:
                l_names.append(l_column_tuple[NAME])
            return l_names
        except Exception as l_error:
            Printer.print("Error fetching column names for table {}: {}".format(p_table_name, l_error), Level.WARNING)

    @staticmethod
    def get_table_column_metadata(p_table_name: str) -> list:
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Fetching column metadata for table {}".format(p_table_name), Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_ONLY)
            l_query = "SELECT * FROM pragma_table_info('{}');".format(p_table_name)
            return SQLite.__execute_query(l_connection, l_query)
        except sqlite3.Error as l_error:
            Printer.print("Error fetching column metadata for table {}: {}".format(p_table_name, l_error), Level.WARNING)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def get_discovered_service_records(l_record_type: Studies) -> list:
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Fetching discovered service records", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_ONLY)
            l_query: str = "SELECT * " \
                           "FROM main.discovered_services " \
                           "WHERE main.discovered_services.study_uniqid = ? " \
                           "ORDER BY port, ipv4_address;"
            l_parameters: tuple = (l_record_type.value,)
            l_records: list = SQLite.__execute_parameterized_query(l_connection, l_query, l_parameters)
            return l_records
        except sqlite3.Error as l_error:
            Printer.print("Error fetching discovered service records: {}".format(l_error), Level.WARNING)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def __convert_epoch_to_string(p_epoch_time: int) -> str:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p_epoch_time))

    @staticmethod
    def get_newer_study_file_records(p_port: int, p_protocol: str, p_timestamp: int) -> list:
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Fetching study file records newer than {}".format(SQLite.__convert_epoch_to_string(p_timestamp)), Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_ONLY)
            # Sort order ensures the most recent file is parsed
            l_query: str = "SELECT " \
                               "filename," \
                               "timestamp," \
                               "protocol," \
                               "port " \
                            "FROM main.study_files " \
                            "WHERE main.study_files.port = ? " \
                            "   AND main.study_files.protocol = ? " \
                            "   AND main.study_files.timestamp > ? " \
                            "ORDER BY year DESC, month DESC, day DESC, port ASC, timestamp DESC;"
            l_parameters: tuple = (p_port, p_protocol, p_timestamp)
            l_records: list = SQLite.__execute_parameterized_query(l_connection, l_query, l_parameters)
            return l_records
        except sqlite3.Error as l_error:
            Printer.print("Error fetching study file records newer than {}".format(SQLite.__convert_epoch_to_string(p_timestamp)), Level.ERROR)
        except Exception as l_error:
            Printer.print("EError fetching newer study file records: {} {}".format(type(l_error).__name__, l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def get_unparsed_study_file_records() -> list:
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Fetching unparsed study file records", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_ONLY)
            # Sort order ensures the most recent file is parsed
            l_query: str = "SELECT " \
                               "study_uniqid," \
                               "filename," \
                               "year," \
                               "month," \
                               "day," \
                               "timestamp," \
                               "protocol," \
                               "port " \
                           "FROM main.study_files " \
                           "WHERE main.study_files.parsed = 'N' " \
                           "ORDER BY year DESC, month DESC, day DESC, port ASC, timestamp DESC;"
            l_records: list = SQLite.__execute_query(l_connection, l_query)
            return l_records
        except sqlite3.Error as l_error:
            Printer.print("Error fetching unparsed study file records: {}".format(l_error), Level.WARNING)
        except Exception as l_error:
            Printer.print("Error fetching unparsed study file records: {} {}".format(type(l_error).__name__, l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def insert_new_study_file_records(p_records: list):
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Inserting study file records", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "INSERT OR IGNORE INTO main.study_files(" \
                               "study_uniqid," \
                               "filename," \
                               "year," \
                               "month," \
                               "day," \
                               "timestamp," \
                               "timestamp_string," \
                               "protocol," \
                               "port" \
                           ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            SQLite.__execute_parameterized_queries(l_connection, l_query, p_records)
        except sqlite3.OperationalError as l_op_error:
            Printer.print("Error inserting unparsed study file records: {}".format(l_op_error), Level.ERROR)
        except sqlite3.Error as l_error:
            Printer.print("Error inserting unparsed study file records: {}".format(l_error), Level.ERROR)
        except Exception as l_error:
            Printer.print("Error inserting unparsed study file records: {} {}".format(type(l_error).__name__, l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def insert_discovered_service_records(p_records: list):
        # timestamp_ts, saddr, sport, daddr, dport, ipid, ttl
        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Inserting discovered service records", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "INSERT OR REPLACE INTO main.discovered_services(" \
                            "ipv4_address," \
                            "port," \
                            "protocol," \
                            "study_uniqid," \
                            "filename," \
                            "organization_name," \
                            "ip_address_range," \
                            "additional_notes," \
                            "discovered_timestamp," \
                            "discovered_timestamp_string," \
                            "parsed_timestamp," \
                            "parsed_timestamp_string" \
                           ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime(?, 'unixepoch', 'localtime'), ?, datetime(?, 'unixepoch', 'localtime'))"
            SQLite.__execute_parameterized_queries(l_connection, l_query, p_records)
        except sqlite3.OperationalError as l_op_error:
            Printer.print("Error inserting discovered service records: {}".format(l_op_error), Level.ERROR)
        except sqlite3.Error as l_error:
            Printer.print("Error inserting discovered service records: {}".format(l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def delete_obsolete_service_records(p_port: int, p_protocol: str):

        l_connection:sqlite3.Connection = None

        try:
            Printer.print("Deleting obsolete service records for port {}_{}".format(p_port, p_protocol), Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "DELETE FROM main.discovered_services WHERE port = ? and protocol = ?;"
            l_parameters: tuple = (p_port, p_protocol)
            SQLite.__execute_parameterized_query(l_connection, l_query, l_parameters)
        except sqlite3.OperationalError as l_op_error:
            Printer.print("Error deleting discovered service records: {}".format(l_op_error), Level.ERROR)
        except sqlite3.Error as l_error:
            Printer.print("Error deleting discovered service records: {}".format(l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def update_obsolete_study_file_records(p_days_until_obsolete: int):
        l_connection: sqlite3.Connection = None
        l_now: int = int(time.mktime(time.localtime()))
        l_obsolete_date: int = l_now - (p_days_until_obsolete * SQLite.SECONDS_PER_DAY)

        try:
            Printer.print("Updating obsolete study file records", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "UPDATE OR IGNORE main.study_files " \
                           "SET parsed = 'O'," \
                               "parsed_timestamp = '{}'," \
                               "parsed_timestamp_string = datetime('{}', 'unixepoch', 'localtime') " \
                           "WHERE " \
                                "timestamp < '{}';".format(l_now, l_now, l_obsolete_date)
            SQLite.__execute_query(l_connection, l_query)

        except sqlite3.Error as l_error:
            Printer.print("Error updating obsolete study file records: {}".format(l_error), Level.WARNING)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def update_parsed_study_file_record(p_filename: str):
        l_connection: sqlite3.Connection = None
        l_now: int = int(time.mktime(time.localtime()))

        try:
            Printer.print("Updating parsed study file record", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "UPDATE OR IGNORE main.study_files " \
                           "SET parsed = 'Y'," \
                               "parsed_timestamp = '{}'," \
                               "parsed_timestamp_string = datetime('{}', 'unixepoch', 'localtime') " \
                           "WHERE " \
                                "filename = '{}';".format(l_now, l_now, p_filename)
            SQLite.__execute_query(l_connection, l_query)

        except sqlite3.Error as l_error:
            Printer.print("Error updating parsed study file record: {}".format(l_error), Level.WARNING)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def update_outdated_study_file_record(p_filename: str):
        l_connection: sqlite3.Connection = None
        l_now: int = int(time.mktime(time.localtime()))

        try:
            Printer.print("Updating outdated study file record since newer study is available: {}".format(p_filename), Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE)
            l_query: str = "UPDATE OR IGNORE main.study_files " \
                           "SET parsed = 'O'," \
                               "parsed_timestamp = '{}'," \
                               "parsed_timestamp_string = datetime('{}', 'unixepoch', 'localtime') " \
                           "WHERE " \
                                "filename = '{}';".format(l_now, l_now, p_filename)
            SQLite.__execute_query(l_connection, l_query)

        except sqlite3.Error as l_error:
            Printer.print("Error updating outdated study file record: {}".format(l_error), Level.WARNING)
        finally:
            if l_connection:
                l_connection.close()

    @staticmethod
    def create_database() -> None:
        l_connection:sqlite3.Connection = None
        try:
            Printer.print("Creating database", Level.INFO)
            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE_CREATE)
            Printer.print("Connected to database", Level.SUCCESS)

            SQLite.__enable_foreign_keys(l_connection)
            SQLite.__create_parse_status_table(l_connection)
            SQLite.__create_study_files_table(l_connection)
            SQLite.__create_discovered_services_table(l_connection)

        # study-uniqid, filename (PK), year, month, day, timestamp, protocol, port, parsed="N"

        except sqlite3.Error as l_error:
            Printer.print("Error creating database: {}".format(l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()