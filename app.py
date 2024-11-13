import sqlite3
import os
import csv
import shutil
import logging

# Set up logging
logging.basicConfig(filename='db_logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def main():
    connection = None
    while True:
        query = input("> ").strip()

        if query.upper() == "EXIT":
            if connection:
                connection.close()
            break

        connection, result = process_query(query, connection)
        if result:
            print(result)

def process_query(query, connection):
    parts = query.split()
    if len(parts) == 0:
        return log_and_return(connection, "No command provided")

    command = parts[0].upper()
    if command == "CREATE":
        if len(parts) > 1 and parts[1].upper() == "DATABASE":
            return create_database(parts[2], connection)
        elif len(parts) > 1 and parts[1].upper() == "TABLE":
            return create_table(query, connection)
        else:
            return log_and_return(connection, "Invalid CREATE command")
    elif command == "USE":
        return use_database(parts[1], connection)
    elif command == "INSERT":
        return insert_into_table(query, connection)
    elif command == "SELECT":
        return select_from_table(query, connection)
    elif command == "UPDATE":
        return update_table(query, connection)
    elif command == "DELETE":
        return delete_from_table(query, connection)
    elif command == "DROP":
        if len(parts) > 1 and parts[1].upper() == "TABLE":
            return drop_table(parts[2], connection)
        elif len(parts) > 1 and parts[1].upper() == "DATABASE":
            return drop_database(parts[2], connection)
        else:
            return log_and_return(connection, "Invalid DROP command")
    elif command == "LIST":
        return list_databases()
    elif command == "SHOW" and len(parts) > 1 and parts[1].upper() == "TABLES":
        return list_tables(connection)
    elif command == "DESCRIBE" and len(parts) > 1:
        return describe_table(parts[1], connection)
    elif command == "EXPORT" and len(parts) > 2:
        return export_table_to_csv(parts[1], parts[2], connection)
    elif command == "IMPORT" and len(parts) > 2:
        return import_table_from_csv(parts[1], parts[2], connection)
    elif command == "BACKUP" and len(parts) > 1:
        return backup_database(parts[1])
    elif command == "RESTORE" and len(parts) > 1:
        return restore_database(parts[1])
    else:
        return log_and_return(connection, "Unknown command")

def log_and_return(connection, message, error=False):
    if error:
        logging.error(message)
    else:
        logging.info(message)
    return connection, message

def create_database(name, connection):
    if connection:
        connection.close()
    os.makedirs("Dbs", exist_ok=True)
    connection = sqlite3.connect(f"Dbs/{name}.db")
    return log_and_return(connection, f"Database {name} created and selected")

def use_database(name, connection):
    if connection:
        connection.close()
    connection = sqlite3.connect(f"Dbs/{name}.db")
    return log_and_return(connection, f"Using database {name}")

def drop_database(db_name, connection):
    if connection:
        connection.close()
        connection = None
    try:
        os.remove(f"Dbs/{db_name}.db")
        return log_and_return(connection, f"Database {db_name} dropped successfully")
    except OSError as e:
        return log_and_return(connection, f"Error dropping database: {e}", error=True)

def create_table(query, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)
    
    try:
        connection.execute(query)
        connection.commit()
        return log_and_return(connection, "Table created successfully")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error creating table: {e}", error=True)

def insert_into_table(query, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        connection.execute(query)
        connection.commit()
        return log_and_return(connection, "Record inserted successfully")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error inserting into table: {e}", error=True)

def select_from_table(query, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        cursor = connection.execute(query)
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
        
        return log_and_return(connection, result)
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error selecting from table: {e}", error=True)

def update_table(query, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        connection.execute(query)
        connection.commit()
        return log_and_return(connection, "Table updated successfully")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error updating table: {e}", error=True)

def delete_from_table(query, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        connection.execute(query)
        connection.commit()
        return log_and_return(connection, "Records deleted successfully")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error deleting from table: {e}", error=True)

def drop_table(table_name, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        connection.execute(f"DROP TABLE {table_name}")
        connection.commit()
        return log_and_return(connection, f"Table {table_name} dropped successfully")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error dropping table: {e}", error=True)

def list_databases():
    try:
        databases = [f.split('.')[0] for f in os.listdir("Dbs") if f.endswith(".db")]
        if databases:
            return log_and_return(None, "\n".join(databases))
        else:
            return log_and_return(None, "No databases found")
    except OSError as e:
        return log_and_return(None, f"Error listing databases: {e}", error=True)

def list_tables(connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)
    
    try:
        cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            table_list = "\n".join(table[0] for table in tables)
            return log_and_return(connection, f"Tables:\n{table_list}")
        else:
            return log_and_return(connection, "No tables found in the current database")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error listing tables: {e}", error=True)

def describe_table(table_name, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)

    try:
        cursor = connection.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if columns:
            schema = "\n".join(f"{col[1]} ({col[2]})" for col in columns)
            return log_and_return(connection, f"Schema of {table_name}:\n{schema}")
        else:
            return log_and_return(connection, f"No table named {table_name} found")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error describing table: {e}", error=True)

def export_table_to_csv(table_name, file_name, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)
    
    try:
        cursor = connection.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            writer.writerows(rows)
        
        return log_and_return(connection, f"Table {table_name} exported to {file_name}")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error exporting table: {e}", error=True)

def import_table_from_csv(table_name, file_name, connection):
    if not connection:
        return log_and_return(connection, "No database selected", error=True)
    
    try:
        with open(file_name, 'r') as csvfile:
            reader = csv.reader(csvfile)
            columns = next(reader)
            rows = list(reader)
        
        placeholders = ', '.join('?' * len(columns))
        columns_str = ', '.join(columns)
        
        connection.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
        connection.executemany(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", rows)
        connection.commit()
        
        return log_and_return(connection, f"Table {table_name} imported from {file_name}")
    except sqlite3.Error as e:
        return log_and_return(connection, f"Error importing table: {e}", error=True)

def backup_database(db_name):
    try:
        src = f"Dbs/{db_name}.db"
        dest = f"Dbs/{db_name}_backup.db"
        shutil.copyfile(src, dest)
        return log_and_return(None, f"Database {db_name} backed up as {db_name}_backup.db")
    except OSError as e:
        return log_and_return(None, f"Error backing up database: {e}", error=True)

def restore_database(db_name):
    try:
        src = f"Dbs/{db_name}_backup.db"
        dest = f"Dbs/{db_name}.db"
        shutil.copyfile(src, dest)
        return log_and_return(None, f"Database {db_name} restored from {db_name}_backup.db")
    except OSError as e:
        return log_and_return(None, f"Error restoring database: {e}", error=True)

if __name__ == "__main__":
    main()
