import sqlite3
from argparser import Parser
from printer import Printer, Level
from urllib.request import pathname2url
from enum import Enum

class Mode(Enum):
    READ_ONLY = 'ro'
    READ_WRITE = 'rw'
    READ_WRITE_CREATE = 'rwc'
    IN_MEMORY = 'memory'

class SQLite():

    ATTACHED_DATABASE_FILENAME: int = 2

    database_filename: str = ""

    @staticmethod
    def __connect_to_database(p_mode: Mode) -> sqlite3.Connection:
        try:
            l_database_file_uri: str = 'file:{}?mode={}'.format(pathname2url(SQLite.database_filename), p_mode.value)
            l_connection: sqlite3.Connection = sqlite3.connect(l_database_file_uri, uri=True)
            Printer.print("Connected to SQLite version {} database".format(sqlite3.sqlite_version), Level.SUCCESS)
            l_query:str = "SELECT * FROM pragma_database_list();"
            l_rows = SQLite.__execute_query(l_connection, l_query)
            for l_row in l_rows:
                Printer.print("Attached database: {}".format(l_row[SQLite.ATTACHED_DATABASE_FILENAME]), Level.INFO)
            return l_connection
        except sqlite3.OperationalError as l_error:
            Printer.print("Error connecting to database: {}".format(l_error), Level.ERROR)

        return None

    @staticmethod
    def __execute_query(p_connection: sqlite3.Connection, p_query: str) -> list:
        try:
            l_cursor: sqlite3.Cursor = p_connection.cursor()
            l_cursor.execute(p_query)
            l_rows: list = l_cursor.fetchall()
            p_connection.commit()
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
    def __get_table_columns(p_connection: sqlite3.Connection, p_table_name: str) -> list:
        l_query = "SELECT * FROM pragma_table_info('{}}');".format(p_table_name)
        return SQLite.__execute_query(p_connection, l_query)

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
    def create_database() -> None:
        l_connection:sqlite3.Connection = None
        try:
            Printer.print("Creating database", Level.SUCCESS)

            l_connection = SQLite.__connect_to_database(Mode.READ_WRITE_CREATE)
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
                              "parsed TEXT DEFAULT 'N' NOT NULL" \
                            ")"
            Printer.print("Creating table study_files", Level.INFO)
            SQLite.__execute_query(l_connection, l_query)
            Printer.print("Created table study_files", Level.SUCCESS)

        # study-uniqid, filename (PK), year, month, day, timestamp, protocol, port, parsed="N"

        except sqlite3.Error as l_error:
            Printer.print("Error creating database: {}".format(l_error), Level.ERROR)
        finally:
            if l_connection:
                l_connection.close()