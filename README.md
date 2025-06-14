# Singlish Chatbot - Sri Lankan English Chat Assistant

A modern, AI-powered chatbot that understands and responds to Sri Lankan English (Singlish) phrases. Built with Nuxt 3, Vue 3, and Tailwind CSS with fuzzy string matching for enhanced understanding.

![Singlish Chatbot Demo](https://img.shields.io/badge/Demo-Live-brightgreen)
![Nuxt 3](https://img.shields.io/badge/Nuxt-3-00C58E)
![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC)

## ✨ Features

### 🗣️ Singlish Understanding
- Recognizes mixed English and Sinhala phrases
- Understands common Sri Lankan expressions like "kohomada", "machan", "nangi"
- Supports variations and colloquialisms

### 🎯 Fuzzy Matching
- Handles typos and spelling variations using fuzzball.js
- "kohomda", "kohomadha", "kohomada" all work perfectly
- Smart intent matching with confidence scoring

### 💬 Modern Chat Interface
- Floating chat widget in bottom-right corner
- Smooth animations and transitions
- Typing indicators and message bubbles
- Unread message notifications
- Mobile-responsive design

### ⚡ Real-time Features
- Instant message processing
- Session-based chat history
- Auto-scroll to latest messages
- Focus management and keyboard shortcuts

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- Yarn or npm package manager

### Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   yarn install
   # or
   npm install
   ```

3. **Run development server:**
   ```bash
   yarn dev
   # or
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🎭 Example Conversations

### Greetings
- **User:** "kohomada bro"
- **Bot:** "Hari honda machan! Oya kohomada? 😊"

### Introductions  
- **User:** "mage nama Susith"
- **Bot:** "Oya susith neda? Hari honda! Mama CoverageBot, oyata help karanna puluwan! 🤖"

### Questions
- **User:** "oyage nama mokakda"
- **Bot:** "Mama CoverageBot! Singlish walata reply karanna puluwan chatbot kenek. Oyata mata kohomada kiyanawa? 😄"

## 🏗️ Project Structure

```
├── components/
│   └── SinglishChatbot.vue    # Main chatbot component
├── data/
│   └── chatbotIntents.js      # Intent definitions and responses
├── assets/
│   └── css/
│       └── main.css           # Tailwind CSS imports
├── app.vue                    # Main application layout
├── nuxt.config.ts             # Nuxt configuration
└── tailwind.config.js         # Tailwind CSS configuration
```

## 🧠 How It Works

### Intent Recognition System
The chatbot uses a sophisticated intent-based matching system:

1. **Phrase Collection:** All possible user inputs are stored with their corresponding intents
2. **Fuzzy Matching:** fuzzball.js compares user input against known phrases
3. **Confidence Scoring:** Only matches above 60% similarity are considered
4. **Response Selection:** The best match triggers the appropriate response

### Supported Intents
- **Greeting:** kohomada, hello, ayubowan, etc.
- **Self Introduction:** mage nama, my name is, etc.
- **Name Inquiry:** oyage nama mokakda, who are you, etc.
- **How Are You:** oya kohomada, how are you, etc.
- **Goodbye:** bye, giya, see you later, etc.
- **Thanks:** thanks, stuti, bohoma stuti, etc.
- **Help:** help karanna, mokak karanne, etc.
- **Weather:** weather mokakda, hawa, rain, etc.
- **Love:** adare, love you, darling, etc.
- **Food:** kanna, bath, rice and curry, etc.

## 🎨 Customization

### Adding New Intents
Edit `data/chatbotIntents.js` to add new conversation patterns:

```javascript
{
  intent: "new_intent_name",
  phrases: [
    "phrase 1", "phrase 2", "variation 1"
  ],
  response: "Bot response with emojis! 😊"
}
```

### Styling Changes
- Edit `tailwind.config.js` for theme customization
- Modify `components/SinglishChatbot.vue` for UI changes
- Update `assets/css/main.css` for global styles

### Fuzzy Matching Sensitivity
Adjust the `cutoff` value in `SinglishChatbot.vue` (line ~185):
```javascript
cutoff: 60 // Lower = more lenient, Higher = stricter
```

## 🛠️ Technical Stack

- **Frontend Framework:** Nuxt 3 with Vue 3 Composition API
- **Styling:** Tailwind CSS with custom animations
- **String Matching:** fuzzball.js for fuzzy text comparison
- **Build Tool:** Vite (included with Nuxt 3)
- **Package Manager:** Yarn (or npm)

## 📱 Mobile Support

The chatbot is fully responsive and works seamlessly on:
- Desktop browsers
- Mobile devices (iOS Safari, Android Chrome)
- Tablets and touch devices

## 🔧 Development

### Available Scripts
```bash
# Development server
yarn dev

# Build for production
yarn build

# Preview production build
yarn preview

# Generate static site
yarn generate
```

### Code Structure
- **Vue 3 Composition API** for reactive state management
- **TypeScript support** out of the box with Nuxt 3
- **ESLint/Prettier** ready (can be added via nuxi)
- **Auto-imports** for Vue composables and utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new intents or improve existing ones
4. Test your changes thoroughly
5. Submit a pull request

### Ideas for Contributions
- Add more Singlish phrases and variations
- Improve fuzzy matching accuracy
- Add voice input/output capabilities
- Create multi-language support
- Add conversation memory/context

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with love for the Sri Lankan tech community
- Inspired by the rich linguistic diversity of Sri Lanka
- Thanks to the open-source community for amazing tools

## 📞 Support

If you encounter any issues or have suggestions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Provide steps to reproduce any bugs

---

**Made with ❤️ for Sri Lanka** 🇱🇰
