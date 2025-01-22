import sqlite3
import json
from typing import Optional, Dict, List
import os
from utils.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            # Ensure the data directory exists
            os.makedirs('data', exist_ok=True)
            self.conn = sqlite3.connect('data/bot.db')
            self.create_tables()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseError("Could not initialize database")

    def create_tables(self):
        """Create necessary tables with error handling."""
        try:
            cursor = self.conn.cursor()
            
            # Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Tweet history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweet_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                input_data TEXT,
                generated_tweets TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            
            # Subscriptions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                tier TEXT NOT NULL,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Table creation error: {e}")
            raise DatabaseError("Could not create database tables")

    def register_user(self, user_id: int, username: str = None, 
                     first_name: str = None, last_name: str = None) -> None:
        """Register or update user information."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = ?,
                first_name = ?,
                last_name = ?,
                last_active = CURRENT_TIMESTAMP
            ''', (user_id, username, first_name, last_name,
                 username, first_name, last_name))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"User registration error: {e}")
            raise DatabaseError("Could not register user")

    def update_last_active(self, user_id: int) -> None:
        """Update user's last active timestamp."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
            ''', (user_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Update last active error: {e}")
            # Don't raise error for this non-critical operation
            pass

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT username, first_name, last_name, preferences, created_at, last_active
            FROM users WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return {
                'username': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'preferences': json.loads(result[3]) if result[3] else None,
                'created_at': result[4],
                'last_active': result[5]
            }
        except sqlite3.Error as e:
            logger.error(f"Get user info error: {e}")
            raise DatabaseError("Could not retrieve user information")

    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT preferences FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return None

    def set_user_preferences(self, user_id: int, preferences: Dict):
        cursor = self.conn.cursor()
        preferences_json = json.dumps(preferences)
        cursor.execute('''
        INSERT INTO users (user_id, preferences) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET preferences = ?
        ''', (user_id, preferences_json, preferences_json))
        self.conn.commit()

    def add_tweet_history(self, user_id: int, input_data: dict, generated_tweets: list):
        """Store generated tweets in history."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweet_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            input_data TEXT,
            generated_tweets TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        cursor.execute('''
        INSERT INTO tweet_history (user_id, input_data, generated_tweets)
        VALUES (?, ?, ?)
        ''', (user_id, json.dumps(input_data), json.dumps(generated_tweets)))
        self.conn.commit()

    def get_user_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Retrieve user's tweet history."""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT input_data, generated_tweets, created_at
        FROM tweet_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'input_data': json.loads(row[0]),
                'generated_tweets': json.loads(row[1]),
                'created_at': row[2]
            })
        return history 