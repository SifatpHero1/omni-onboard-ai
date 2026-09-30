import sqlite3
from typing import Optional, List, Dict
from pathlib import Path
from src.utils.logger import logger

class DatabaseClient:
    """SQLite database client for client management"""
    
    def __init__(self, db_path: str = "data/onboarding.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE NOT NULL,
                contact_person TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                service_tier TEXT NOT NULL,
                monthly_value REAL NOT NULL,
                requirements TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def check_company_exists(self, company_name: str) -> bool:
        """Check if a company already exists in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM clients WHERE LOWER(company_name) = LOWER(?)",
            (company_name,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def insert_client(self, client_data: Dict) -> int:
        """Insert a new client into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clients (
                company_name, contact_person, contact_email,
                service_tier, monthly_value, requirements, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_data['company_name'],
            client_data['contact_person'],
            client_data['contact_email'],
            client_data['service_tier'],
            client_data['monthly_value'],
            client_data.get('requirements'),
            'active'
        ))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Inserted client: {client_data['company_name']} (ID: {client_id})")
        return client_id
    
    def log_audit(self, email_id: str, action: str, details: str = None):
        """Log an audit entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log (email_id, action, details)
            VALUES (?, ?, ?)
        """, (email_id, action, details))
        
        conn.commit()
        conn.close()
    
    def get_all_clients(self) -> List[Dict]:
        """Get all clients from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clients ORDER BY created_at DESC")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]