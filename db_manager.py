import sqlite3
import os
import csv
import shutil
import logging
from typing import Tuple, Optional, Any

class DatabaseManager:
    def __init__(self):
        """
        Manages the database connection and processes queries
        """
        self.connection = None
        logging.basicConfig(filename='db_logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
    
    def get_connection(self):
        """
        Returns a connection to the current database
        """
        if self.connection is None:
            raise Exception("No database selected")
        return sqlite3.connect(self.connection)
    
    def close_connection(self):
        """
        Closes the connection to the current database
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def process_query(self, query: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Processes the given query and returns the result
        Args:
            query: The SQL query to process
        """
        if not query:
            return self.log_and_return(self.connection, "No command provided")

        try:
            parts = query.split()
            if len(parts) == 0:
                return self.log_and_return(self.connection, "No command provided")

            command = parts[0].upper()
            if command == "CREATE":
                if len(parts) > 1 and parts[1].upper() == "DATABASE":
                    return self.create_database(parts[2])
                elif len(parts) > 1 and parts[1].upper() == "TABLE":
                    return self.create_table(query)
                else:
                    return self.log_and_return(self.connection, "Invalid CREATE command")
            elif command == "USE":
                return self.use_database(parts[1])
            elif command == "INSERT":
                return self.insert_into_table(query)
            elif command == "SELECT":
                return self.select_from_table(query)
            elif command == "UPDATE":
                return self.update_table(query)
            elif command == "DELETE":
                return self.delete_from_table(query)
            elif command == "DROP":
                if len(parts) > 1 and parts[1].upper() == "TABLE":
                    return self.drop_table(parts[2])
                elif len(parts) > 1 and parts[1].upper() == "DATABASE":
                    return self.drop_database(parts[2])
                else:
                    return self.log_and_return(self.connection, "Invalid DROP command")
            elif command == "LIST":
                return self.list_databases()
            elif command == "SHOW" and len(parts) > 1 and parts[1].upper() == "TABLES":
                return self.list_tables()
            elif command == "DESCRIBE" and len(parts) > 1:
                return self.describe_table(parts[1])
            elif command == "EXPORT" and len(parts) > 2:
                return self.export_table_to_csv(parts[1], parts[2])
            elif command == "IMPORT" and len(parts) > 2:
                return self.import_table_from_csv(parts[1], parts[2])
            elif command == "BACKUP" and len(parts) > 1:
                return self.backup_database(parts[1])
            elif command == "RESTORE" and len(parts) > 1:
                return self.restore_database(parts[1])
            else:
                return self.log_and_return(self.connection, "Unknown command")
        except Exception as e:
            return self.log_and_return(self.connection, f"Error processing query: {str(e)}", error=True)

    def log_and_return(self, connection: Optional[sqlite3.Connection], message: str, error: bool = False) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Logs the given message and returns it along with the connection
        Args:
            connection: The connection to return
            message: The message to log and return
            error: Whether the message is an error message
        """
        if error:
            logging.error(message)
        else:
            logging.info(message)
        return connection, message

    def create_database(self, name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Creates a new database with the given name and selects it
        Args:
            name: The name of the database to create
        """
        if self.connection:
            self.connection.close()
        os.makedirs("Dbs", exist_ok=True)
        self.connection = f"Dbs/{name}.db"
        return self.log_and_return(f"Database {name} created and selected")

    def use_database(self, name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Selects the database with the given name
        Args:
            name: The name of the database to select
        """
        self.connection = f"Dbs/{name}.db"
        return self.log_and_return(self.connection, f"Using database {name}")
    
    def drop_database(self, db_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Drops the database with the given name
        Args:  
            db_name: The name of the database to drop
        """
        self.close_connection()
        try:
            os.remove(f"Dbs/{db_name}.db")
            return self.log_and_return(self.connection, f"Database {db_name} dropped successfully")
        except OSError as e:
            return self.log_and_return(self.connection, f"Error dropping database: {e}", error=True)

    def create_table(self, query) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Creates a table with the given schema
        Args:
            query: The CREATE TABLE query to execute
        """
        conn = self.get_connection()
        try:
            conn.execute(query)
            conn.commit()
            return self.log_and_return(conn, "Table created successfully")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error creating table: {e}", error=True)
        finally:
            conn.close()

    def insert_into_table(self, query) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Inserts a record into the table
        Args:
            query: The INSERT INTO query to execute
        """
        conn = self.get_connection()
        try:
            conn.execute(query)
            conn.commit()
            return self.log_and_return(conn, "Record inserted successfully")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error inserting into table: {e}", error=True)
        finally:
            conn.close()

    def select_from_table(self, query) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Selects records from the table
        Args:
            query: The SELECT query to execute
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            if rows:
                max_lengths = [max(len(str(item)) for item in col) for col in zip(columns, *rows)]
                header = ' | '.join(f"{col.ljust(max_len)}" for col, max_len in zip(columns, max_lengths))
                separator = '-+-'.join('-' * max_len for max_len in max_lengths)
                data = '\n'.join(' | '.join(str(item).ljust(max_len) for item, max_len in zip(row, max_lengths)) for row in rows)
                result = f"{header}\n{separator}\n{data}"
            else:
                result = "No records found"
            return self.log_and_return(conn, result)
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error selecting from table: {e}", error=True)
        finally:
            conn.close()

    def update_table(self, query) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Updates records in the table
        Args:
            query: The UPDATE query to execute
        """
        conn = self.get_connection()
        try:
            conn.execute(query)
            conn.commit()
            return self.log_and_return(conn, "Table updated successfully")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error updating table: {e}", error=True)
        finally:
            conn.close()

    def delete_from_table(self, query) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Deletes records from the table
        Args:
            query: The DELETE query to execute
        """
        conn = self.get_connection()
        try:
            conn.execute(query)
            conn.commit()
            return self.log_and_return(conn, "Records deleted successfully")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error deleting from table: {e}", error=True)
        finally:
            conn.close()

    def drop_table(self, table_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Drops the table with the given name
        Args:   
            table_name: The name of the table to drop
        """
        conn = self.get_connection()
        try:
            conn.execute(f"DROP TABLE {table_name}")
            conn.commit()
            return self.log_and_return(conn, f"Table {table_name} dropped successfully")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error dropping table: {e}", error=True)
        finally:
            conn.close()

    def list_databases(self) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Lists all databases in the Dbs directory
        """
        try:
            databases = [f.split('.')[0] for f in os.listdir("Dbs") if f.endswith(".db") and not f.endswith("_backup.db")]
            if databases:
                return self.log_and_return(None, "\n".join(databases))
            else:
                return self.log_and_return(None, "No databases found")
        except OSError as e:
            return self.log_and_return(None, f"Error listing databases: {e}", error=True)

    def list_tables(self) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Lists all tables in the current database
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                table_list = "\n".join(table[0] for table in tables)
                return self.log_and_return(conn, f"|Tables|\n{table_list}")
            else:
                return self.log_and_return(conn, "No tables found in the current database")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error listing tables: {e}", error=True)
        finally:
            conn.close()

    def describe_table(self, table_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Describes the schema of the table with the given name
        Args:
            table_name: The name of the table to describe
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            if columns:
                schema = "\n".join(f"{col[1]} ({col[2]})" for col in columns)
                return self.log_and_return(conn, f"|Schema of {table_name}|\n{schema}")
            else:
                return self.log_and_return(conn, f"No table named {table_name} found")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error describing table: {e}", error=True)
        finally:
            conn.close()

    def export_table_to_csv(self, table_name: str, file_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Exports the table with the given name to a CSV file
        Args:
            table_name: The name of the table to export
            file_name: The name of the CSV file to export to
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(rows)
            
            return self.log_and_return(conn, f"Table {table_name} exported to {file_name}")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error exporting table: {e}", error=True)
        finally:
            conn.close()

    def import_table_from_csv(self, table_name: str, file_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Imports the table from the given CSV file
        Args:
            table_name: The name of the table to import
            file_name: The name of the CSV file to import from
        """
        conn = self.get_connection()
        try:
            with open(file_name, 'r') as csvfile:
                reader = csv.reader(csvfile)
                columns = next(reader)
                rows = list(reader)
            
            placeholders = ', '.join('?' * len(columns))
            columns_str = ', '.join(columns)
            
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
            conn.executemany(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", rows)
            conn.commit()
            
            return self.log_and_return(conn, f"Table {table_name} imported from {file_name}")
        except sqlite3.Error as e:
            return self.log_and_return(conn, f"Error importing table: {e}", error=True)
        finally:
            conn.close()

    def backup_database(self, db_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Backs up the database with the given name
        Args:
            db_name: The name of the database to backup
        """
        try:
            src = f"Dbs/{db_name}.db"
            dest = f"Dbs/{db_name}_backup.db"
            shutil.copyfile(src, dest)
            return self.log_and_return(None, f"Database {db_name} backed up as {db_name}_backup.db")
        except OSError as e:
            return self.log_and_return(None, f"Error backing up database: {e}", error=True)

    def restore_database(self, db_name: str) -> Tuple[Optional[sqlite3.Connection], str]:
        """
        Restores the database with the given name from the backup
        Args:
            db_name: The name of the database to restore
        """
        try:
            src = f"Dbs/{db_name}_backup.db"
            dest = f"Dbs/{db_name}.db"
            shutil.copyfile(src, dest)
            return self.log_and_return(None, f"Database {db_name} restored from {db_name}_backup.db")
        except OSError as e:
            return self.log_and_return(None, f"Error restoring database: {e}", error=True)