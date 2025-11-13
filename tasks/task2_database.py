import mysql.connector
from mysql.connector import Error
import csv
import os
from dotenv import load_dotenv

load_dotenv()


class JobDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'jobs_db')
        
    def connect(self):
        """Connect to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.cursor.execute(f"USE {self.database}")
            
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def create_table(self):
        """Create jobs table if it doesn't exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    location VARCHAR(255),
                    salary VARCHAR(255),
                    job_type VARCHAR(100),
                    description TEXT,
                    posted_date VARCHAR(100),
                    job_url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_job (title, company, location)
                )
            ''')
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error creating table: {e}")
            return False
    
    def load_from_csv(self, csv_file='indeed_jobs.csv'):
        if not os.path.exists(csv_file):
            return {'success': False, 'error': 'CSV file not found', 'inserted': 0, 'duplicates': 0}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                inserted_count = 0
                duplicate_count = 0
                
                for row in csv_reader:
                    try:
                        self.cursor.execute('''
                            INSERT INTO jobs (title, company, location, salary, job_type, description, posted_date, job_url)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            row.get('title', 'N/A'),
                            row.get('company', 'N/A'),
                            row.get('location', 'N/A'),
                            row.get('salary', 'N/A'),
                            row.get('job_type', 'N/A'),
                            row.get('description', 'N/A'),
                            row.get('posted_date', 'N/A'),
                            row.get('job_url', 'N/A')
                        ))
                        inserted_count += 1
                    except Error as e:
                        if e.errno == 1062:  
                            duplicate_count += 1
                        continue
                
                self.connection.commit()
                
                return {
                    'success': True,
                    'inserted': inserted_count,
                    'duplicates': duplicate_count
                }
                
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': str(e), 'inserted': 0, 'duplicates': 0}
    
    def get_all_jobs(self):
        try:
            self.cursor.execute('SELECT * FROM jobs')
            jobs = self.cursor.fetchall()
            return jobs
        except Error as e:
            print(f"Error retrieving jobs: {e}")
            return []
    
    def get_job_count(self):
        try:
            self.cursor.execute('SELECT COUNT(*) FROM jobs')
            count = self.cursor.fetchone()[0]
            return count
        except Error as e:
            print(f"Error counting jobs: {e}")
            return 0
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()


def load_to_database(csv_file='indeed_jobs.csv'):
    db = JobDatabase()
    
    try:
        if not db.connect():
            return {'success': False, 'error': 'Database connection failed. Check your .env file and MySQL server.'}
        
        if not db.create_table():
            return {'success': False, 'error': 'Failed to create table'}
        
        result = db.load_from_csv(csv_file)
        total_jobs = db.get_job_count()
        result['total'] = total_jobs
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
