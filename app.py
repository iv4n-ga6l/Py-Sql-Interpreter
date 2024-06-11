import sqlite3
import os

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
        return connection, "No command provided"

    command = parts[0].upper()
    if command == "CREATE":
        if len(parts) > 1 and parts[1].upper() == "DATABASE":
            return create_database(parts[2], connection)
        elif len(parts) > 1 and parts[1].upper() == "TABLE":
            return create_table(query, connection)
        else:
            return connection, "Invalid CREATE command"
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
            return connection, "Invalid DROP command"
    elif command == "LIST":
        return list_databases()
    else:
        return connection, "Unknown command"

def create_database(name, connection):
    if connection:
        connection.close()
    os.makedirs("Dbs", exist_ok=True)
    connection = sqlite3.connect(f"Dbs/{name}.db")
    return connection, f"Database {name} created and selected"

def use_database(name, connection):
    if connection:
        connection.close()
    connection = sqlite3.connect(f"Dbs/{name}.db")
    return connection, f"Using database {name}"

def drop_database(db_name, connection):
    if connection:
        connection.close()
        connection = None
    try:
        os.remove(f"Dbs/{db_name}.db")
        return connection, f"Database {db_name} dropped successfully"
    except OSError as e:
        return connection, f"Error dropping database: {e}"

def create_table(query, connection):
    if not connection:
        return connection, "No database selected"
    
    try:
        connection.execute(query)
        connection.commit()
        return connection, "Table created successfully"
    except sqlite3.Error as e:
        return connection, f"Error creating table: {e}"

def insert_into_table(query, connection):
    if not connection:
        return connection, "No database selected"

    try:
        connection.execute(query)
        connection.commit()
        return connection, "Record inserted successfully"
    except sqlite3.Error as e:
        return connection, f"Error inserting into table: {e}"

def select_from_table(query, connection):
    if not connection:
        return connection, "No database selected"

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
        
        return connection, result
    except sqlite3.Error as e:
        return connection, f"Error selecting from table: {e}"

def update_table(query, connection):
    if not connection:
        return connection, "No database selected"

    try:
        connection.execute(query)
        connection.commit()
        return connection, "Table updated successfully"
    except sqlite3.Error as e:
        return connection, f"Error updating table: {e}"

def delete_from_table(query, connection):
    if not connection:
        return connection, "No database selected"

    try:
        connection.execute(query)
        connection.commit()
        return connection, "Records deleted successfully"
    except sqlite3.Error as e:
        return connection, f"Error deleting from table: {e}"

def drop_table(table_name, connection):
    if not connection:
        return connection, "No database selected"

    try:
        connection.execute(f"DROP TABLE {table_name}")
        connection.commit()
        return connection, f"Table {table_name} dropped successfully"
    except sqlite3.Error as e:
        return connection, f"Error dropping table: {e}"

def list_databases():
    try:
        databases = [f.split('.')[0] for f in os.listdir("Dbs") if f.endswith(".db")]
        if databases:
            return None, "\n".join(databases)
        else:
            return None, "No databases found"
    except OSError as e:
        return None, f"Error listing databases: {e}"

if __name__ == "__main__":
    main()
