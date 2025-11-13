from flask import Blueprint, jsonify, request
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

api_bp = Blueprint('api', __name__)


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'jobs_db')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def dict_from_row(row, columns):
    """Convert MySQL row to dictionary."""
    return {
        'id': row[0],
        'title': row[1],
        'company': row[2],
        'location': row[3],
        'salary': row[4],
        'job_type': row[5],
        'description': row[6],
        'posted_date': row[7],
        'job_url': row[8],
        'scraped_at': row[9]
    }


@api_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    """GET /api/jobs - Return all job listings with optional filters."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        city = request.args.get('city', '').strip()
        position = request.args.get('position', '').strip()
        
        query = 'SELECT * FROM jobs WHERE 1=1'
        params = []
        
        if city:
            query += ' AND location LIKE %s'
            params.append(f'%{city}%')
        
        if position:
            query += ' AND title LIKE %s'
            params.append(f'%{position}%')
        
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        jobs_list = [dict_from_row(job, columns) for job in jobs]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(jobs_list),
            'jobs': jobs_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """GET /api/jobs/<id> - Return details for a specific job."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if job:
            columns = ['id', 'title', 'company', 'location', 'salary', 'job_type', 'description', 'posted_date', 'job_url', 'scraped_at']
            return jsonify({
                'success': True,
                'job': dict_from_row(job, columns)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/jobs', methods=['POST'])
def add_job():
    """POST /api/jobs - Add a new job entry."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'company' not in data:
            return jsonify({
                'success': False,
                'error': 'Title and company are required fields'
            }), 400
        
        title = data.get('title')
        company = data.get('company')
        location = data.get('location', 'N/A')
        salary = data.get('salary', 'N/A')
        job_type = data.get('job_type', 'N/A')
        description = data.get('description', 'N/A')
        posted_date = data.get('posted_date', 'N/A')
        job_url = data.get('job_url', 'N/A')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jobs (title, company, location, salary, job_type, description, posted_date, job_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (title, company, location, salary, job_type, description, posted_date, job_url))
        
        conn.commit()
        job_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Job added successfully',
            'job_id': job_id
        }), 201
        
    except Error as e:
        if e.errno == 1062:  
            return jsonify({
                'success': False,
                'error': 'Job already exists'
            }), 409
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """PUT /api/jobs/<id> - Update existing job details."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        update_fields = []
        params = []
        
        allowed_fields = ['title', 'company', 'location', 'salary', 'job_type', 'description', 'posted_date', 'job_url']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f'{field} = %s')
                params.append(data[field])
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        params.append(job_id)
        
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Job updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """DELETE /api/jobs/<id> - Delete a job entry."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        cursor.execute('DELETE FROM jobs WHERE id = %s', (job_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
