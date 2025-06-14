import express from 'express';
import Joi from 'joi';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { getDB } from '../database/connection.js';
import { logger } from '../utils/logger.js';
import { optionalAuthMiddleware } from '../middleware/auth.js';
import { cacheGet, cacheSet } from '../config/redis.js';

const router = express.Router();

// Validation schemas
const messageSchema = Joi.object({
  message: Joi.string().min(1).max(1000).required(),
  sessionId: Joi.string().uuid().optional()
});

// Process chat message
router.post('/message', optionalAuthMiddleware, async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Validate input
    const { error, value } = messageSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        success: false,
        error: error.details[0].message
      });
    }

    const { message, sessionId } = value;
    const userId = req.user?.id || null;
    const db = getDB();

    // Create or get session
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = uuidv4();
      
      // Create new session if user is authenticated
      if (userId) {
        await db.query(
          'INSERT INTO chat_sessions (id, user_id, session_name) VALUES ($1, $2, $3)',
          [currentSessionId, userId, `Chat ${new Date().toLocaleDateString()}`]
        );
      }
    }

    // Store user message
    const userMessageId = uuidv4();
    if (userId) {
      await db.query(
        `INSERT INTO messages (id, session_id, user_id, message_type, content) 
         VALUES ($1, $2, $3, 'user', $4)`,
        [userMessageId, currentSessionId, userId, message]
      );
    }

    // Get response from ML service or fallback to rule-based
    let botResponse;
    let intentDetected = null;
    let confidenceScore = null;

    try {
      // Try ML service first
      if (process.env.ML_SERVICE_URL) {
        const mlResponse = await axios.post(`${process.env.ML_SERVICE_URL}/predict`, {
          message: message.toLowerCase(),
          user_id: userId,
          session_id: currentSessionId
        }, {
          timeout: 5000,
          headers: {
            'Authorization': `Bearer ${process.env.ML_SERVICE_API_KEY || 'development'}`
          }
        });

        botResponse = mlResponse.data.response;
        intentDetected = mlResponse.data.intent;
        confidenceScore = mlResponse.data.confidence;
      }
    } catch (mlError) {
      logger.warn('ML service unavailable, falling back to rule-based response:', mlError.message);
    }

    // Fallback to rule-based response if ML service failed
    if (!botResponse) {
      const fallbackResponse = await getRuleBasedResponse(message.toLowerCase());
      botResponse = fallbackResponse.response;
      intentDetected = fallbackResponse.intent;
      confidenceScore = fallbackResponse.confidence;
    }

    const responseTime = Date.now() - startTime;

    // Store bot response
    const botMessageId = uuidv4();
    if (userId) {
      await db.query(
        `INSERT INTO messages (id, session_id, user_id, message_type, content, intent_detected, confidence_score, response_time_ms) 
         VALUES ($1, $2, $3, 'bot', $4, $5, $6, $7)`,
        [botMessageId, currentSessionId, userId, botResponse, intentDetected, confidenceScore, responseTime]
      );
    }

    // Log analytics
    if (userId) {
      await db.query(
        `INSERT INTO user_analytics (user_id, session_id, event_type, event_data, ip_address, user_agent) 
         VALUES ($1, $2, 'message_sent', $3, $4, $5)`,
        [
          userId, 
          currentSessionId, 
          JSON.stringify({ 
            intent: intentDetected, 
            confidence: confidenceScore, 
            response_time: responseTime 
          }),
          req.ip,
          req.get('User-Agent')
        ]
      );
    }

    res.json({
      success: true,
      data: {
        sessionId: currentSessionId,
        response: botResponse,
        intent: intentDetected,
        confidence: confidenceScore,
        responseTime: responseTime,
        messageId: botMessageId
      }
    });

  } catch (error) {
    logger.error('Chat message error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process message'
    });
  }
});

// Get chat history
router.get('/history/:sessionId', optionalAuthMiddleware, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user?.id;
    const db = getDB();

    let query;
    let params;

    if (userId) {
      // Get history for authenticated user
      query = `
        SELECT id, message_type, content, intent_detected, confidence_score, created_at
        FROM messages 
        WHERE session_id = $1 AND user_id = $2
        ORDER BY created_at ASC
      `;
      params = [sessionId, userId];
    } else {
      // For anonymous users, we can't retrieve history from database
      return res.json({
        success: true,
        data: {
          messages: [],
          sessionId
        }
      });
    }

    const result = await db.query(query, params);

    res.json({
      success: true,
      data: {
        messages: result.rows.map(row => ({
          id: row.id,
          type: row.message_type,
          content: row.content,
          intent: row.intent_detected,
          confidence: row.confidence_score,
          timestamp: row.created_at
        })),
        sessionId
      }
    });

  } catch (error) {
    logger.error('Get chat history error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve chat history'
    });
  }
});

// Get user's chat sessions
router.get('/sessions', optionalAuthMiddleware, async (req, res) => {
  try {
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required'
      });
    }

    const db = getDB();
    const result = await db.query(
      `SELECT cs.id, cs.session_name, cs.created_at, cs.updated_at,
              COUNT(m.id) as message_count,
              MAX(m.created_at) as last_message_at
       FROM chat_sessions cs
       LEFT JOIN messages m ON cs.id = m.session_id
       WHERE cs.user_id = $1 AND cs.is_active = true
       GROUP BY cs.id, cs.session_name, cs.created_at, cs.updated_at
       ORDER BY COALESCE(MAX(m.created_at), cs.created_at) DESC
       LIMIT 50`,
      [userId]
    );

    res.json({
      success: true,
      data: {
        sessions: result.rows.map(row => ({
          id: row.id,
          name: row.session_name,
          messageCount: parseInt(row.message_count),
          lastMessageAt: row.last_message_at,
          createdAt: row.created_at,
          updatedAt: row.updated_at
        }))
      }
    });

  } catch (error) {
    logger.error('Get sessions error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve sessions'
    });
  }
});

// Rule-based response fallback (using your existing intents)
async function getRuleBasedResponse(userInput) {
  try {
    // Check cache first
    const cacheKey = `intent:${userInput}`;
    const cached = await cacheGet(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Import your existing intents
    const { chatbotIntents } = await import('../../data/chatbotIntents.js');
    
    // Simple fuzzy matching (you can enhance this)
    let bestMatch = null;
    let bestScore = 0;
    
    for (const intent of chatbotIntents) {
      for (const phrase of intent.phrases) {
        const similarity = calculateSimilarity(userInput, phrase.toLowerCase());
        if (similarity > bestScore && similarity > 0.6) {
          bestScore = similarity;
          bestMatch = {
            response: intent.response,
            intent: intent.intent,
            confidence: similarity
          };
        }
      }
    }

    if (!bestMatch) {
      bestMatch = {
        response: "Mata eka therenne naha machan! Try 'kohomada' or 'help' kiyla! 🤔",
        intent: "unknown",
        confidence: 0
      };
    }

    // Cache the result
    await cacheSet(cacheKey, bestMatch, 3600); // Cache for 1 hour
    
    return bestMatch;
    
  } catch (error) {
    logger.error('Rule-based response error:', error);
    return {
      response: "Sorry, I'm having trouble understanding. Please try again! 😅",
      intent: "error",
      confidence: 0
    };
  }
}

// Simple similarity calculation (you can use fuzzball here too)
function calculateSimilarity(str1, str2) {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) {
    return 1.0;
  }
  
  return (longer.length - editDistance(longer, shorter)) / longer.length;
}

function editDistance(str1, str2) {
  const matrix = [];
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[str2.length][str1.length];
}

export default router;