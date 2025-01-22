from enum import Enum
from typing import Optional
from datetime import datetime, timedelta
import json

class SubscriptionTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

class SubscriptionManager:
    def __init__(self, db):
        self.db = db
        self.setup_subscription_table()
    
    def setup_subscription_table(self):
        """Create subscription table if it doesn't exist."""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            tier TEXT NOT NULL,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        self.db.conn.commit()
    
    def get_user_subscription(self, user_id: int) -> SubscriptionTier:
        """Get user's current subscription tier."""
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT tier, expires_at FROM subscriptions 
        WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return SubscriptionTier.FREE
        return SubscriptionTier(result[0])
    
    def set_premium_subscription(self, user_id: int, duration_days: int = 30):
        """Set or extend premium subscription."""
        cursor = self.db.conn.cursor()
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        cursor.execute('''
        INSERT INTO subscriptions (user_id, tier, expires_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
            tier = ?, 
            expires_at = MAX(expires_at, ?)
        ''', (
            user_id, 
            SubscriptionTier.PREMIUM.value, 
            expires_at,
            SubscriptionTier.PREMIUM.value,
            expires_at
        ))
        self.db.conn.commit() 