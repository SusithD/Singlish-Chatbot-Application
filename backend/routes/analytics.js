import express from 'express';
import { getDB } from '../database/connection.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get user analytics dashboard
router.get('/dashboard', async (req, res) => {
  try {
    const userId = req.user.id;
    const db = getDB();

    // Get overall stats
    const statsResult = await db.query(
      `SELECT 
        COUNT(DISTINCT cs.id) as total_sessions,
        COUNT(m.id) as total_messages,
        COUNT(CASE WHEN m.message_type = 'user' THEN 1 END) as user_messages,
        COUNT(CASE WHEN m.message_type = 'bot' THEN 1 END) as bot_messages,
        AVG(m.response_time_ms) as avg_response_time,
        MIN(cs.created_at) as first_chat_date
       FROM chat_sessions cs
       LEFT JOIN messages m ON cs.id = m.session_id
       WHERE cs.user_id = $1`,
      [userId]
    );

    // Get intent distribution
    const intentResult = await db.query(
      `SELECT intent_detected, COUNT(*) as count
       FROM messages 
       WHERE user_id = $1 AND intent_detected IS NOT NULL
       GROUP BY intent_detected
       ORDER BY count DESC
       LIMIT 10`,
      [userId]
    );

    // Get recent activity (last 7 days)
    const activityResult = await db.query(
      `SELECT DATE(created_at) as date, COUNT(*) as message_count
       FROM messages
       WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
       GROUP BY DATE(created_at)
       ORDER BY date DESC`,
      [userId]
    );

    const stats = statsResult.rows[0];
    
    res.json({
      success: true,
      data: {
        overview: {
          totalSessions: parseInt(stats.total_sessions) || 0,
          totalMessages: parseInt(stats.total_messages) || 0,
          userMessages: parseInt(stats.user_messages) || 0,
          botMessages: parseInt(stats.bot_messages) || 0,
          avgResponseTime: parseFloat(stats.avg_response_time) || 0,
          firstChatDate: stats.first_chat_date
        },
        intents: intentResult.rows.map(row => ({
          intent: row.intent_detected,
          count: parseInt(row.count)
        })),
        recentActivity: activityResult.rows.map(row => ({
          date: row.date,
          messageCount: parseInt(row.message_count)
        }))
      }
    });

  } catch (error) {
    logger.error('Analytics dashboard error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve analytics'
    });
  }
});

// Get conversation insights
router.get('/insights', async (req, res) => {
  try {
    const userId = req.user.id;
    const db = getDB();

    // Get most active hours
    const hoursResult = await db.query(
      `SELECT EXTRACT(HOUR FROM created_at) as hour, COUNT(*) as count
       FROM messages
       WHERE user_id = $1 AND message_type = 'user'
       GROUP BY EXTRACT(HOUR FROM created_at)
       ORDER BY count DESC`,
      [userId]
    );

    // Get confidence score distribution
    const confidenceResult = await db.query(
      `SELECT 
         CASE 
           WHEN confidence_score >= 0.8 THEN 'high'
           WHEN confidence_score >= 0.6 THEN 'medium'
           ELSE 'low'
         END as confidence_level,
         COUNT(*) as count
       FROM messages
       WHERE user_id = $1 AND confidence_score IS NOT NULL
       GROUP BY confidence_level`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        activeHours: hoursResult.rows.map(row => ({
          hour: parseInt(row.hour),
          count: parseInt(row.count)
        })),
        confidenceDistribution: confidenceResult.rows.map(row => ({
          level: row.confidence_level,
          count: parseInt(row.count)
        }))
      }
    });

  } catch (error) {
    logger.error('Analytics insights error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve insights'
    });
  }
});

export default router;