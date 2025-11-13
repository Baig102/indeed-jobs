from flask import Flask, render_template, request, jsonify
from tasks.task1_scraper import run_scraper
from tasks.task2_database import load_to_database
from tasks.task3_api import api_bp
import os

app = Flask(__name__)
app.register_blueprint(api_bp)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/task1')
def task1_page():
    return render_template('task1_scraper.html')


@app.route('/task2')
def task2_page():
    return render_template('task2_database.html')


@app.route('/task3')
def task3_page():
    return render_template('task3_api.html')


@app.route('/run-scraper', methods=['POST'])
def run_scraper_endpoint():
    try:
        data = request.get_json()
        position = data.get('position', '').strip()
        city = data.get('city', '').strip()
        date_posted = data.get('date_posted', '').strip()
        max_pages = int(data.get('max_pages', 5))
        
        if not position or not city:
            return jsonify({
                'success': False,
                'error': 'Position and city are required'
            }), 400
        
        result = run_scraper(position, city, date_posted, max_pages)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/load-database', methods=['POST'])
def load_database_endpoint():
    try:
        if not os.path.exists('indeed_jobs.csv'):
            return jsonify({
                'success': False,
                'error': 'No CSV file found. Please run the scraper first.'
            }), 400
        
        result = load_to_database()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/stats')
def get_stats():
    """Get system statistics."""
    import mysql.connector
    from dotenv import load_dotenv
    
    load_dotenv()
    
    stats = {
        'csv_exists': os.path.exists('indeed_jobs.csv'),
        'db_exists': False,
        'total_jobs': 0
    }
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'jobs_db')
        )
        stats['db_exists'] = True
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except:
        pass
    
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
