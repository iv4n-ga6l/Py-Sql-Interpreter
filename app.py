import argparse
import os
from routes import app, db_manager

def cli_mode():
    print("[SQL Interpreter] --- Type 'EXIT' to quit.")
    while True:
        try:
            query = input("> ").strip()
            if query.upper() == "EXIT":
                # db_manager.close_connection()
                break
            if not query:
                continue

            _, result = db_manager.process_query(query)
            if result:
                print(result)
        except KeyboardInterrupt:
            print("\nExiting...")
            if db_manager.connection:
                db_manager.connection.close()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SQL Interpreter')
    parser.add_argument('--mode', choices=['web', 'cli'], default='web', help='Run in web or CLI mode (default: web)')
    args = parser.parse_args()

    # Create Dbs directory if it doesn't exist
    if not os.path.exists('Dbs'):
        os.makedirs('Dbs')

    try:
        if args.mode == 'web':
            app.run(debug=True)
        else:
            cli_mode()
    except KeyboardInterrupt:
        print("\nShutting down...")
        db_manager.close_connection()