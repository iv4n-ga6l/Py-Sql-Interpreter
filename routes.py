from flask import Flask, render_template, request, jsonify
from db_manager import DatabaseManager
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