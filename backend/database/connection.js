import pg from 'pg';
import { logger } from '../utils/logger.js';

const { Pool } = pg;

let pool;

export const connectDB = async () => {
  try {
    pool = new Pool({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'singlish_chatbot',
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    // Test the connection
    const client = await pool.connect();
    await client.query('SELECT NOW()');
    client.release();

    logger.info('PostgreSQL connected successfully');
    
    // Initialize database tables
    await initializeTables();
    
  } catch (error) {
    logger.error('PostgreSQL connection failed:', error);
    throw error;
  }
};

export const getDB = () => {
  if (!pool) {
    throw new Error('Database not connected. Call connectDB first.');
  }
  return pool;
};

const initializeTables = async () => {
  const client = await pool.connect();
  
  try {
    // Create extensions
    await client.query('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"');
    
    // Users table
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        avatar_url TEXT,
        is_verified BOOLEAN DEFAULT FALSE,
        preferences JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    // Chat sessions table
    await client.query(`
      CREATE TABLE IF NOT EXISTS chat_sessions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        session_name VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    // Messages table
    await client.query(`
      CREATE TABLE IF NOT EXISTS messages (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'bot')),
        content TEXT NOT NULL,
        intent_detected VARCHAR(100),
        confidence_score DECIMAL(3,2),
        response_time_ms INTEGER,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    // Intents table (for dynamic intent management)
    await client.query(`
      CREATE TABLE IF NOT EXISTS intents (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        phrases TEXT[] NOT NULL,
        responses TEXT[] NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        category VARCHAR(50),
        priority INTEGER DEFAULT 1,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    // User analytics table
    await client.query(`
      CREATE TABLE IF NOT EXISTS user_analytics (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
        event_type VARCHAR(50) NOT NULL,
        event_data JSONB DEFAULT '{}',
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    // Create indexes for performance
    await client.query('CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)');
    await client.query('CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics(user_id)');

    logger.info('Database tables initialized successfully');
    
  } catch (error) {
    logger.error('Failed to initialize database tables:', error);
    throw error;
  } finally {
    client.release();
  }
};

export const closeDB = async () => {
  if (pool) {
    await pool.end();
    logger.info('Database connection closed');
  }
};