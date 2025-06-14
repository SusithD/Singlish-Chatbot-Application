import express from 'express';
import Joi from 'joi';
import { getDB } from '../database/connection.js';
import { logger } from '../utils/logger.js';
import { cacheDelete } from '../config/redis.js';

const router = express.Router();

// Validation schemas
const intentSchema = Joi.object({
  name: Joi.string().min(1).max(100).required(),
  description: Joi.string().max(500).optional(),
  phrases: Joi.array().items(Joi.string().min(1).max(200)).min(1).required(),
  responses: Joi.array().items(Joi.string().min(1).max(1000)).min(1).required(),
  category: Joi.string().max(50).optional(),
  priority: Joi.number().integer().min(1).max(10).default(1)
});

// Get all intents
router.get('/', async (req, res) => {
  try {
    const db = getDB();
    const result = await db.query(
      `SELECT id, name, description, phrases, responses, is_active, category, priority, created_at, updated_at
       FROM intents 
       WHERE is_active = true
       ORDER BY priority DESC, name ASC`
    );

    res.json({
      success: true,
      data: {
        intents: result.rows.map(row => ({
          id: row.id,
          name: row.name,
          description: row.description,
          phrases: row.phrases,
          responses: row.responses,
          isActive: row.is_active,
          category: row.category,
          priority: row.priority,
          createdAt: row.created_at,
          updatedAt: row.updated_at
        }))
      }
    });

  } catch (error) {
    logger.error('Get intents error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve intents'
    });
  }
});

// Create new intent
router.post('/', async (req, res) => {
  try {
    // Validate input
    const { error, value } = intentSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        success: false,
        error: error.details[0].message
      });
    }

    const { name, description, phrases, responses, category, priority } = value;
    const userId = req.user.id;
    const db = getDB();

    // Check if intent name already exists
    const existing = await db.query(
      'SELECT id FROM intents WHERE name = $1',
      [name]
    );

    if (existing.rows.length > 0) {
      return res.status(400).json({
        success: false,
        error: 'Intent with this name already exists'
      });
    }

    // Create intent
    const result = await db.query(
      `INSERT INTO intents (name, description, phrases, responses, category, priority, created_by)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING id, name, description, phrases, responses, category, priority, created_at`,
      [name, description, phrases, responses, category, priority, userId]
    );

    // Clear intent cache
    await cacheDelete('intent:*');

    logger.info(`New intent created: ${name} by user ${userId}`);

    res.status(201).json({
      success: true,
      data: {
        intent: result.rows[0]
      }
    });

  } catch (error) {
    logger.error('Create intent error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create intent'
    });
  }
});

// Update intent
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { error, value } = intentSchema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        success: false,
        error: error.details[0].message
      });
    }

    const { name, description, phrases, responses, category, priority } = value;
    const db = getDB();

    // Check if intent exists
    const existing = await db.query(
      'SELECT id FROM intents WHERE id = $1',
      [id]
    );

    if (existing.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Intent not found'
      });
    }

    // Update intent
    const result = await db.query(
      `UPDATE intents 
       SET name = $1, description = $2, phrases = $3, responses = $4, 
           category = $5, priority = $6, updated_at = NOW()
       WHERE id = $7
       RETURNING id, name, description, phrases, responses, category, priority, updated_at`,
      [name, description, phrases, responses, category, priority, id]
    );

    // Clear intent cache
    await cacheDelete('intent:*');

    res.json({
      success: true,
      data: {
        intent: result.rows[0]
      }
    });

  } catch (error) {
    logger.error('Update intent error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update intent'
    });
  }
});

// Delete intent
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const db = getDB();

    // Soft delete (mark as inactive)
    const result = await db.query(
      'UPDATE intents SET is_active = false, updated_at = NOW() WHERE id = $1 RETURNING id',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Intent not found'
      });
    }

    // Clear intent cache
    await cacheDelete('intent:*');

    res.json({
      success: true,
      message: 'Intent deleted successfully'
    });

  } catch (error) {
    logger.error('Delete intent error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete intent'
    });
  }
});

export default router;