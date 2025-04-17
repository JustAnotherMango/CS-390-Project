from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from auth import create_access_token, decode_access_token
import mysql.connector
import logging

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'root',  # Replace with your MySQL password
    'database': 'trades_db'
}

def get_db_connection():
    try:
        logger.info("Attempting to connect to MySQL database...")
        conn = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def fetch_all_from_table(table_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        logger.info(f"Executing query: SELECT * FROM {table_name}")
        cursor.execute(f"SELECT * FROM {table_name}")
        results = cursor.fetchall()
        logger.info(f"Retrieved {len(results)} records from {table_name}")
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error fetching data from {table_name}: {e}")
        raise

@app.route('/')
def index():
    logger.info("Root endpoint accessed")
    return jsonify({
        'status': 'API is running',
        'routes': [
            '/Users',
            '/Politicians',
            '/StockMarketData',
            '/API_Requests',
            '/Trades',
            '/Confidence'
        ]
    })

@app.route('/test-db-connection')
def test_db_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "success", "message": "Database connection successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/Users')
def get_users():
    try:
        return jsonify(fetch_all_from_table('Users'))
    except Exception as e:
        logger.error(f"Error in /Users endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/Politicians')
def get_politicians():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM politician_trades")
    trades = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"trades": trades})


@app.route('/StockMarketData')
def get_stock_market_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM StockMarketData")
        results = cursor.fetchall()
        
        # Convert TIME objects to strings for JSON serialization
        for row in results:
            if 'Open' in row and hasattr(row['Open'], 'isoformat'):
                row['Open'] = row['Open'].isoformat()
            if 'Close' in row and hasattr(row['Close'], 'isoformat'):
                row['Close'] = row['Close'].isoformat()
            if 'Date' in row and hasattr(row['Date'], 'isoformat'):
                row['Date'] = row['Date'].isoformat()
        
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in /StockMarketData endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/API_Requests')
def get_api_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM API_Requests")
        results = cursor.fetchall()
        
        # Convert TIME objects to strings for JSON serialization
        for row in results:
            if 'RequestTime' in row and hasattr(row['RequestTime'], 'isoformat'):
                row['RequestTime'] = row['RequestTime'].isoformat()
        
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in /API_Requests endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/Trades')
def get_trades():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Trades")
        results = cursor.fetchall()
        
        # Convert DATE objects to strings for JSON serialization
        for row in results:
            if 'TradeDate' in row and hasattr(row['TradeDate'], 'isoformat'):
                row['TradeDate'] = row['TradeDate'].isoformat()
            if 'Date' in row and hasattr(row['Date'], 'isoformat'):
                row['Date'] = row['Date'].isoformat()
        
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in /Trades endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/Confidence')
def get_confidence():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Confidence")
        results = cursor.fetchall()
        
        # Convert TIME objects to strings for JSON serialization
        for row in results:
            if 'TimeStamp' in row and hasattr(row['TimeStamp'], 'isoformat'):
                row['TimeStamp'] = row['TimeStamp'].isoformat()
        
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in /Confidence endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user['password'] == password:
            token = create_access_token({"sub": username})
            response = make_response(jsonify({"message": "Login successful"}))
            response.set_cookie(
                "access_token",
                token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24,
                path="/"
            )
            return response
            # return jsonify({"message": "Login successful", "user_id": user['id']}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
        
    except Exception as e:
        logger.error(f"Error in /login endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie(
        'access_token',
        '',
        expires=0,
        max_age=0,
        httponly=True,
        samesite='Lax',
        secure=False,
        path='/'
    )
    return response

@app.route('/me', methods=['GET'])
def me():
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401
    
    payload = decode_access_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({"username": payload.get("sub")})

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True)

