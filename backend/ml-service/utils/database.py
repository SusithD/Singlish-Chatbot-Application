import psycopg2
import redis
import json
from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database management for ML service"""
    
    def __init__(self):
        self.db_pool = None
        self.redis_client = None
        
    async def connect(self):
        """Connect to databases"""
        try:
            # PostgreSQL connection
            self.db_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', 5432),
                database=os.getenv('DB_NAME', 'singlish_chatbot'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD')
            )
            
            # Redis connection
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=os.getenv('REDIS_PORT', 6379),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            
            logger.info("✅ Database connections established")
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise e
    
    def is_connected(self) -> bool:
        """Check if databases are connected"""
        try:
            if self.db_pool:
                conn = self.db_pool.getconn()
                self.db_pool.putconn(conn)
                return True
            return False
        except:
            return False
    
    async def store_interaction(
        self,
        user_id: str,
        session_id: str,
        message: str,
        intent: str,
        confidence: float,
        response: str,
        processing_time: float
    ):
        """Store ML interaction data"""
        try:
            if not self.db_pool:
                return
                
            conn = self.db_pool.getconn()
            cur = conn.cursor()
            
            # Store ML-specific analytics
            cur.execute("""
                INSERT INTO ml_interactions 
                (user_id, session_id, message, intent, confidence, response, processing_time, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, session_id, message, intent, confidence, response, processing_time, datetime.now()))
            
            conn.commit()
            cur.close()
            self.db_pool.putconn(conn)
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    async def get_performance_analytics(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get ML model performance analytics"""
        try:
            if not self.db_pool:
                return {}
                
            conn = self.db_pool.getconn()
            cur = conn.cursor()
            
            # Calculate date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            # Get analytics data
            cur.execute("""
                SELECT 
                    AVG(confidence) as avg_confidence,
                    AVG(processing_time) as avg_processing_time,
                    COUNT(*) as total_interactions,
                    COUNT(DISTINCT user_id) as unique_users,
                    intent,
                    COUNT(*) as intent_count
                FROM ml_interactions 
                WHERE created_at BETWEEN %s AND %s
                GROUP BY intent
                ORDER BY intent_count DESC
            """, (start_date, end_date))
            
            results = cur.fetchall()
            
            analytics = {
                "period": {"start": start_date, "end": end_date},
                "overall": {
                    "avg_confidence": 0.0,
                    "avg_processing_time": 0.0,
                    "total_interactions": 0,
                    "unique_users": 0
                },
                "intent_distribution": []
            }
            
            if results:
                analytics["overall"]["avg_confidence"] = float(results[0][0] or 0)
                analytics["overall"]["avg_processing_time"] = float(results[0][1] or 0)
                analytics["overall"]["total_interactions"] = sum(row[5] for row in results)
                analytics["overall"]["unique_users"] = results[0][3] or 0
                
                for row in results:
                    analytics["intent_distribution"].append({
                        "intent": row[4],
                        "count": row[5],
                        "percentage": (row[5] / analytics["overall"]["total_interactions"]) * 100
                    })
            
            cur.close()
            self.db_pool.putconn(conn)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}

class CacheManager:
    """Cache management for ML service"""
    
    def __init__(self):
        self.redis_client = None
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=os.getenv('REDIS_PORT', 6379),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            logger.info("✅ Cache manager connected")
        except Exception as e:
            logger.error(f"Cache connection error: {e}")
    
    def is_connected(self) -> bool:
        """Check if cache is connected"""
        try:
            return self.redis_client and self.redis_client.ping()
        except:
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            if self.redis_client:
                return self.redis_client.get(key)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")