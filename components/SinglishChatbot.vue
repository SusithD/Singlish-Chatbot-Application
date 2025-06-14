<template>
  <div class="fixed bottom-4 right-4 z-50">
    <!-- Chat Widget -->
    <div 
      v-if="isOpen" 
      class="bg-white rounded-2xl shadow-2xl w-80 h-96 flex flex-col mb-4 animate-slide-up border border-gray-200"
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-t-2xl flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            🤖
          </div>
          <div>
            <h3 class="font-semibold text-sm">CoverageBot</h3>
            <p class="text-xs opacity-90">Singlish Chat Assistant</p>
          </div>
        </div>
        <button 
          @click="closeChat"
          class="hover:bg-white hover:bg-opacity-20 rounded-full p-1 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Messages Container -->
      <div 
        ref="messagesContainer"
        class="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50"
      >
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="animate-fade-in"
        >
          <!-- User Message -->
          <div v-if="message.type === 'user'" class="flex justify-end">
            <div class="bg-blue-500 text-white px-4 py-2 rounded-2xl rounded-br-md max-w-xs break-words">
              {{ message.text }}
            </div>
          </div>
          
          <!-- Bot Message -->
          <div v-else class="flex justify-start">
            <div class="bg-white border border-gray-200 px-4 py-2 rounded-2xl rounded-bl-md max-w-xs break-words shadow-sm">
              {{ message.text }}
            </div>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTyping" class="flex justify-start animate-fade-in">
          <div class="bg-white border border-gray-200 px-4 py-2 rounded-2xl rounded-bl-md shadow-sm">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
        <div class="flex space-x-2">
          <input
            ref="messageInput"
            v-model="currentMessage"
            @keyup.enter="sendMessage"
            @input="handleInput"
            type="text"
            placeholder="Type in Singlish... (e.g., kohomada?)"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          />
          <button
            @click="sendMessage"
            :disabled="!currentMessage.trim() || isTyping"
            class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-full transition-colors flex items-center justify-center min-w-[40px]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Toggle Button -->
    <button
      @click="toggleChat"
      class="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
      :class="{ 'animate-bounce-in': !hasInteracted }"
    >
      <div v-if="!isOpen" class="text-2xl">💬</div>
      <div v-else class="text-xl">✕</div>
      
      <!-- Notification Badge -->
      <div 
        v-if="unreadCount > 0 && !isOpen"
        class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center animate-pulse"
      >
        {{ unreadCount }}
      </div>
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { extract } from 'fuzzball'
import { chatbotIntents } from '~/data/chatbotIntents.js'

// Reactive state
const isOpen = ref(false)
const messages = ref([])
const currentMessage = ref('')
const isTyping = ref(false)
const hasInteracted = ref(false)
const unreadCount = ref(0)
const messagesContainer = ref(null)
const messageInput = ref(null)

// Welcome message
onMounted(() => {
  messages.value.push({
    id: Date.now(),
    type: 'bot',
    text: 'Ayubowan! Mama CoverageBot. Singlish walata reply karanna puluwan! Try "kohomada" kiyla! 😊',
    timestamp: new Date()
  })
})

// Chat functions
const toggleChat = () => {
  isOpen.value = !isOpen.value
  hasInteracted.value = true
  
  if (isOpen.value) {
    unreadCount.value = 0
    nextTick(() => {
      if (messageInput.value) {
        messageInput.value.focus()
      }
      scrollToBottom()
    })
  }
}

const closeChat = () => {
  isOpen.value = false
}

const handleInput = () => {
  // Add any input handling logic here if needed
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isTyping.value) return

  const userMessage = {
    id: Date.now(),
    type: 'user',
    text: currentMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const userInput = currentMessage.value.trim().toLowerCase()
  currentMessage.value = ''

  await nextTick()
  scrollToBottom()

  // Show typing indicator
  isTyping.value = true
  
  // Simulate typing delay
  setTimeout(() => {
    const botResponse = getBotResponse(userInput)
    
    messages.value.push({
      id: Date.now() + 1,
      type: 'bot',
      text: botResponse,
      timestamp: new Date()
    })

    isTyping.value = false
    
    // If chat is closed, increment unread count
    if (!isOpen.value) {
      unreadCount.value++
    }

    nextTick(() => {
      scrollToBottom()
    })
  }, 1000 + Math.random() * 1000) // Random delay between 1-2 seconds
}

const getBotResponse = (userInput) => {
  const allPhrases = []
  
  // Create a flat array of all phrases with their intent info
  chatbotIntents.forEach(intent => {
    intent.phrases.forEach(phrase => {
      allPhrases.push({
        phrase: phrase.toLowerCase(),
        intent: intent.intent,
        response: intent.response
      })
    })
  })

  // Use fuzzball to find the best matches
  const matches = extract(userInput, allPhrases.map(p => p.phrase), {
    scorer: 'ratio',
    processor: 'default',
    limit: 5,
    cutoff: 60 // Minimum similarity threshold
  })

  if (matches.length > 0) {
    // Find the corresponding response for the best match
    const bestMatch = matches[0]
    const matchedPhrase = allPhrases.find(p => p.phrase === bestMatch[0])
    
    if (matchedPhrase) {
      return matchedPhrase.response
    }
  }

  // Default responses for unmatched input
  const defaultResponses = [
    "Mata eka therenne naha machan! Try 'kohomada' or 'oyage nama mokakda' kiyla! 🤔",
    "Hmm, mata eka understand karanna baha. Simple Singlish walata try karanna! 😅",
    "Aiyo, mata confused! 'Help' kiyla mata kiyanna puluwan de mokakda karanne! 🤷‍♂️",
    "Eka mata clear naha machan. Try 'hello' or 'thanks' wage simple words! 💭"
  ]

  return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
/* Custom scrollbar for messages container */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>