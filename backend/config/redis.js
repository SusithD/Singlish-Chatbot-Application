import { createClient } from 'redis';
import { logger } from '../utils/logger.js';

let redisClient;

export const connectRedis = async () => {
  try {
    redisClient = createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD || undefined,
      retry_strategy: (options) => {
        if (options.error && options.error.code === 'ECONNREFUSED') {
          logger.error('Redis server is not running');
          return new Error('Redis server is not running');
        }
        if (options.total_retry_time > 1000 * 60 * 60) {
          return new Error('Redis retry time exhausted');
        }
        if (options.attempt > 10) {
          return undefined;
        }
        return Math.min(options.attempt * 100, 3000);
      }
    });

    redisClient.on('error', (err) => {
      logger.error('Redis Client Error:', err);
    });

    redisClient.on('connect', () => {
      logger.info('Redis connected successfully');
    });

    await redisClient.connect();
    
  } catch (error) {
    logger.error('Redis connection failed:', error);
    // Don't throw error to allow app to run without Redis
    logger.warn('Application will continue without Redis caching');
  }
};

export const getRedis = () => {
  return redisClient;
};

// Cache utility functions
export const cacheGet = async (key) => {
  if (!redisClient || !redisClient.isOpen) {
    return null;
  }
  try {
    return await redisClient.get(key);
  } catch (error) {
    logger.error('Redis GET error:', error);
    return null;
  }
};

export const cacheSet = async (key, value, expireInSeconds = 3600) => {
  if (!redisClient || !redisClient.isOpen) {
    return false;
  }
  try {
    await redisClient.setEx(key, expireInSeconds, JSON.stringify(value));
    return true;
  } catch (error) {
    logger.error('Redis SET error:', error);
    return false;
  }
};

export const cacheDelete = async (key) => {
  if (!redisClient || !redisClient.isOpen) {
    return false;
  }
  try {
    await redisClient.del(key);
    return true;
  } catch (error) {
    logger.error('Redis DELETE error:', error);
    return false;
  }
};

export const closeRedis = async () => {
  if (redisClient && redisClient.isOpen) {
    await redisClient.quit();
    logger.info('Redis connection closed');
  }
};