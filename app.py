from flask import Flask, render_template, request, jsonify
from db_manager import DatabaseManager
import argparse
import os

app = Flask(__name__)
db_manager = DatabaseManager()

@app.route('/')
def index():
    # Check if templates directory exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_query():
    query = request.json.get('query')
    if not query:
        return jsonify({'result': 'No query provided'}), 400

    _, result = db_manager.process_query(query)
    return jsonify({'result': result})

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