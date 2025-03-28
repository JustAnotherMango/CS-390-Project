from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'localhost',
    'user': '',
    'password': ';',
    'database': 'my_api'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


def fetch_all_from_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


@app.route('/')
def index():
    return jsonify({
        'routes': [
            '/Users',
            '/Politicians',
            '/StockMarketData',
            '/API_Requests',
            '/Trades',
            'Confidence'
        ]
    })

@app.route('/Users')
def get_users():
    return jsonify(fetch_all_from_table('Users'))

@app.route('/Politicians')
def get_politicians():
    return jsonify(fetch_all_from_table('Politicians'))

@app.route('/StockMarketData')
def get_stock_market_data():
    return jsonify(fetch_all_from_table('StockMarketData'))

@app.route('/API_Requests')
def get_api_requests():
    return jsonify(fetch_all_from_table('API_Requests'))

@app.route('/Trades')
def get_trades():
    return jsonify(fetch_all_from_table('Trades'))

@app.route('/Confidence')
def get_confidence():
    return jsonify(fetch_all_from_table('Confidence'))

if __name__ == '__main__':
    app.run(debug=True)
