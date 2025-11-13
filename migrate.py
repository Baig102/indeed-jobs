"""
Database Migration Script
Creates the database and table if they don't exist
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'jobs_db')
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        
        # Switch to the database
        cursor.execute(f"USE {db_name}")
        
        create_table_query = """
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
        """
        cursor.execute(create_table_query)
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        return False
    
    return True

if __name__ == "__main__":
    create_database()
