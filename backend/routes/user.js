import express from 'express';
import { getDB } from '../database/connection.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get user profile
router.get('/profile', async (req, res) => {
  try {
    const userId = req.user.id;
    const db = getDB();
    
    const result = await db.query(
      'SELECT id, email, username, first_name, last_name, avatar_url, is_verified, preferences, created_at FROM users WHERE id = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: result.rows[0]
      }
    });

  } catch (error) {
    logger.error('Get user profile error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve user profile'
    });
  }
});

// Update user preferences
router.put('/preferences', async (req, res) => {
  try {
    const userId = req.user.id;
    const { preferences } = req.body;
    const db = getDB();

    await db.query(
      'UPDATE users SET preferences = $1, updated_at = NOW() WHERE id = $2',
      [JSON.stringify(preferences), userId]
    );

    res.json({
      success: true,
      message: 'Preferences updated successfully'
    });

  } catch (error) {
    logger.error('Update preferences error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update preferences'
    });
  }
});

export default router;