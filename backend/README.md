# 🚀 Singlish Chatbot Backend - Complete Setup Guide

## 📋 **System Architecture Overview**

Your Singlish chatbot now has a powerful, production-ready backend with these components:

### **🏗️ Architecture Components:**
1. **Node.js API Server** (Port 3001) - Main backend with REST API & WebSocket
2. **Python ML Service** (Port 8001) - Advanced NLP and machine learning
3. **PostgreSQL Database** - User data, conversations, analytics
4. **Redis Cache** - Session management and caching
5. **Frontend Integration** - Enhanced Vue.js chatbot

---

## ⚡ **Quick Start (Development)**

### **1. Prerequisites**
```bash
# Install required software
- Node.js (v18+)
- Python (v3.9+)
- PostgreSQL (v13+)
- Redis (v6+)
```

### **2. Database Setup**
```bash
# Create PostgreSQL database
createdb singlish_chatbot

# The backend will auto-create tables on first run
```

### **3. Backend API Setup**
```bash
cd backend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Start the backend
npm run dev
```

### **4. ML Service Setup**
```bash
cd backend/ml-service

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start ML service
python main.py
```

### **5. Start Redis & PostgreSQL**
```bash
# Redis (if not running)
redis-server

# PostgreSQL (if not running)
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

---

## 🎯 **API Endpoints Reference**

### **Authentication (Port 3001)**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

### **Chat (Port 3001)**
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/:sessionId` - Get chat history
- `GET /api/chat/sessions` - Get user's chat sessions

### **Analytics (Port 3001)**
- `GET /api/analytics/dashboard` - User analytics
- `GET /api/analytics/insights` - Conversation insights

### **ML Service (Port 8001)**
- `POST /predict` - Get AI response
- `POST /train` - Train models
- `GET /analytics/performance` - ML performance metrics
- `GET /models/status` - Model status

---

## 🔧 **Configuration Guide**

### **Environment Variables**

#### **Backend (.env)**
```bash
# Core Settings
NODE_ENV=development
PORT=3001
HOST=0.0.0.0

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=singlish_chatbot
DB_USER=postgres
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
JWT_SECRET=your_super_secret_key
JWT_EXPIRES_IN=7d

# ML Service
ML_SERVICE_URL=http://localhost:8001
ML_SERVICE_API_KEY=development_key

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=900000

# External APIs (Optional)
OPENAI_API_KEY=your_openai_key
```

#### **ML Service (.env)**
```bash
ML_SERVICE_API_KEY=development_key
DB_HOST=localhost
DB_NAME=singlish_chatbot
DB_USER=postgres
DB_PASSWORD=your_password
REDIS_HOST=localhost
LOG_LEVEL=INFO
```

---

## 🌟 **Key Features Implemented**

### **🤖 Advanced AI Capabilities**
- **Intent Detection**: ML-powered intent classification
- **Singlish Processing**: Specialized Singlish language understanding
- **Context Awareness**: Conversation context and memory
- **Fuzzy Matching**: Handles typos and variations
- **Response Generation**: Intelligent, contextual responses

### **👥 User Management**
- **Authentication**: JWT-based secure authentication
- **User Profiles**: Comprehensive user management
- **Session Management**: Multi-session chat support
- **Preferences**: Customizable user preferences

### **📊 Analytics & Insights**
- **Real-time Analytics**: Live conversation metrics
- **Performance Tracking**: ML model performance monitoring
- **User Behavior**: Detailed user interaction analysis
- **Intent Distribution**: Popular intent tracking

### **🚀 Performance & Scalability**
- **Caching**: Redis-powered response caching
- **Rate Limiting**: API protection and throttling
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed application logging
- **WebSocket Support**: Real-time communication

---

## 🔄 **Integration with Frontend**

### **Update Your Vue.js Chatbot**

Add this to your `SinglishChatbot.vue`:

```javascript
// Add to your existing component
const API_BASE = 'http://localhost:3001/api'
const userToken = ref(null)

// Enhanced sendMessage function
const sendMessage = async () => {
  if (!currentMessage.value.trim() || isTyping.value) return

  const userMessage = {
    id: Date.now(),
    type: 'user',
    text: currentMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const userInput = currentMessage.value.trim()
  currentMessage.value = ''
  isTyping.value = true

  try {
    // Call backend API
    const response = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(userToken.value && { 'Authorization': `Bearer ${userToken.value}` })
      },
      body: JSON.stringify({
        message: userInput,
        sessionId: sessionId.value
      })
    })

    const data = await response.json()
    
    if (data.success) {
      sessionId.value = data.data.sessionId
      
      messages.value.push({
        id: Date.now() + 1,
        type: 'bot',
        text: data.data.response,
        timestamp: new Date(),
        intent: data.data.intent,
        confidence: data.data.confidence
      })
    } else {
      throw new Error(data.error)
    }
  } catch (error) {
    console.error('Chat error:', error)
    // Fallback to your existing getBotResponse
    const botResponse = getBotResponse(userInput)
    messages.value.push({
      id: Date.now() + 1,
      type: 'bot',
      text: botResponse,
      timestamp: new Date()
    })
  }

  isTyping.value = false
  nextTick(() => scrollToBottom())
}
```

---

## 🧪 **Testing Your Backend**

### **Health Checks**
```bash
# Check API health
curl http://localhost:3001/health

# Check ML service health
curl http://localhost:8001/health
```

### **Test Chat API**
```bash
# Send test message
curl -X POST http://localhost:3001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "kohomada machan"}'
```

### **Test ML Service**
```bash
# Test ML prediction
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer development_key" \
  -d '{"message": "kohomada"}'
```

---

## 🚀 **Production Deployment**

### **Environment Setup**
1. **Set production environment variables**
2. **Use proper database credentials**
3. **Configure HTTPS/SSL**
4. **Set up proper CORS origins**
5. **Use strong JWT secrets**

### **Docker Support** (Optional)
```dockerfile
# Dockerfile for API service
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

### **Process Management**
```bash
# Using PM2 for production
npm install -g pm2
pm2 start server.js --name "singlish-chatbot-api"
pm2 start ml-service/main.py --name "singlish-ml-service" --interpreter python
```

---

## 📈 **Monitoring & Maintenance**

### **Logs Location**
- API logs: `backend/logs/`
- ML service logs: Console output
- Database logs: PostgreSQL logs

### **Performance Monitoring**
- Monitor API response times
- Track ML model accuracy
- Watch database performance
- Monitor Redis cache hit rates

---

## 🎉 **What's Next?**

Your chatbot now has enterprise-grade capabilities:

✅ **Advanced ML-powered responses**
✅ **User authentication and profiles**  
✅ **Real-time chat with WebSocket**
✅ **Comprehensive analytics**
✅ **Scalable architecture**
✅ **Production-ready setup**

### **Suggested Enhancements:**
1. **Voice Integration** - Add speech-to-text
2. **Multi-language Support** - Expand beyond Singlish
3. **Admin Dashboard** - Web interface for management
4. **Mobile App** - React Native or Flutter app
5. **Advanced Analytics** - Machine learning insights

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**Database Connection Issues:**
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Reset database
dropdb singlish_chatbot
createdb singlish_chatbot
```

**ML Service Not Starting:**
```bash
# Check Python environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port Conflicts:**
```bash
# Check what's using ports
lsof -i :3001
lsof -i :8001

# Kill processes if needed
kill -9 <PID>
```

Your Singlish chatbot backend is now ready for production! 🎉