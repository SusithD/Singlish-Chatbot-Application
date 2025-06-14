import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createServer } from 'http';
import { Server } from 'socket.io';
import dotenv from 'dotenv';

// Import our modules
import { logger } from './utils/logger.js';
import { connectDB } from './database/connection.js';
import { connectRedis } from './config/redis.js';
import { errorHandler } from './middleware/errorHandler.js';
import { authMiddleware } from './middleware/auth.js';

// Import routes
import authRoutes from './routes/auth.js';
import chatRoutes from './routes/chat.js';
import userRoutes from './routes/user.js';
import analyticsRoutes from './routes/analytics.js';
import intentRoutes from './routes/intents.js';

// Load environment variables
dotenv.config();

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true
  }
});

// Security middleware
app.use(helmet());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  }
});

app.use(limiter);

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/user', authMiddleware, userRoutes);
app.use('/api/analytics', authMiddleware, analyticsRoutes);
app.use('/api/intents', authMiddleware, intentRoutes);

// WebSocket connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);

  // Join user to their personal room for notifications
  socket.on('join-user-room', (userId) => {
    socket.join(`user-${userId}`);
    logger.info(`User ${userId} joined their room`);
  });

  // Handle real-time chat messages
  socket.on('chat-message', async (data) => {
    try {
      // Process the message and emit response
      const { userId, message, sessionId } = data;
      
      // Emit typing indicator
      socket.to(`user-${userId}`).emit('typing', { sessionId });
      
      // Process message (this would call your ML service)
      // For now, we'll emit a simple response
      setTimeout(() => {
        socket.emit('chat-response', {
          sessionId,
          message: 'Response from backend!',
          timestamp: new Date().toISOString()
        });
      }, 1000);
      
    } catch (error) {
      logger.error('WebSocket chat error:', error);
      socket.emit('chat-error', { error: 'Failed to process message' });
    }
  });

  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// Start server
const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || '0.0.0.0';

async function startServer() {
  try {
    // Connect to database
    await connectDB();
    logger.info('Database connected successfully');

    // Connect to Redis
    await connectRedis();
    logger.info('Redis connected successfully');

    // Start server
    server.listen(PORT, HOST, () => {
      logger.info(`🚀 Singlish Chatbot Backend running on http://${HOST}:${PORT}`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
    });

  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

startServer();

export { app, io };