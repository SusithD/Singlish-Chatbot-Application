import jwt from 'jsonwebtoken';
import { getDB } from '../database/connection.js';
import { logger } from '../utils/logger.js';

export const authMiddleware = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'No token provided, authorization denied'
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Get user from database
    const db = getDB();
    const result = await db.query(
      'SELECT id, email, username, first_name, last_name, is_verified FROM users WHERE id = $1',
      [decoded.userId]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({
        success: false,
        error: 'Token is valid but user not found'
      });
    }

    // Add user to request
    req.user = result.rows[0];
    next();
    
  } catch (error) {
    logger.error('Auth middleware error:', error);
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        error: 'Token expired'
      });
    }
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        error: 'Invalid token'
      });
    }
    
    res.status(500).json({
      success: false,
      error: 'Server error during authentication'
    });
  }
};

// Optional auth middleware (doesn't fail if no token)
export const optionalAuthMiddleware = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      req.user = null;
      return next();
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const db = getDB();
    const result = await db.query(
      'SELECT id, email, username, first_name, last_name, is_verified FROM users WHERE id = $1',
      [decoded.userId]
    );

    req.user = result.rows.length > 0 ? result.rows[0] : null;
    next();
    
  } catch (error) {
    // If token is invalid, just continue without user
    req.user = null;
    next();
  }
};