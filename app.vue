<template>
  <div>
    <!-- Main Content Area -->
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <!-- Header -->
      <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span class="text-white text-xl">🤖</span>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Singlish Chatbot Demo</h1>
                <p class="text-sm text-gray-600">AI-powered Sri Lankan English chat assistant</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="text-center mb-12">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            Welcome to the Singlish Chatbot! 
            <span class="wave">👋</span>
          </h2>
          <p class="text-xl text-gray-600 mb-8">
            Chat with our AI in Sri Lankan English (Singlish) - Try phrases like "kohomada", "oyage nama mokakda", or just say "hello"!
          </p>
        </div>

        <!-- Features Grid -->
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <div class="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <span class="text-2xl">💬</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Singlish Understanding</h3>
            <p class="text-gray-600">Understands mixed English and Sinhala phrases like "kohomada bro" or "hari honda nangi"</p>
          </div>

          <div class="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <span class="text-2xl">🎯</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Fuzzy Matching</h3>
            <p class="text-gray-600">Handles typos and variations in spelling - "kohomda" or "kohomadha" both work!</p>
          </div>

          <div class="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <span class="text-2xl">⚡</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Real-time Chat</h3>
            <p class="text-gray-600">Instant responses with typing indicators and smooth animations</p>
          </div>
        </div>

        <!-- Example Phrases -->
        <div class="bg-white rounded-lg p-8 shadow-md mb-12">
          <h3 class="text-2xl font-bold text-gray-900 mb-6 text-center">Try These Phrases:</h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-semibold text-gray-900 mb-3">Greetings:</h4>
              <ul class="space-y-2 text-gray-600">
                <li><code class="bg-gray-100 px-2 py-1 rounded">kohomada</code> - How are you?</li>
                <li><code class="bg-gray-100 px-2 py-1 rounded">kohomada bro</code> - How are you bro?</li>
                <li><code class="bg-gray-100 px-2 py-1 rounded">ayubowan</code> - Traditional greeting</li>
              </ul>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 mb-3">Questions:</h4>
              <ul class="space-y-2 text-gray-600">
                <li><code class="bg-gray-100 px-2 py-1 rounded">oyage nama mokakda</code> - What's your name?</li>
                <li><code class="bg-gray-100 px-2 py-1 rounded">mage nama Susith</code> - My name is Susith</li>
                <li><code class="bg-gray-100 px-2 py-1 rounded">help karanna</code> - Help me</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Call to Action -->
        <div class="text-center">
          <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-8 text-white">
            <h3 class="text-2xl font-bold mb-4">Ready to Chat?</h3>
            <p class="text-lg mb-6">Click the chat button in the bottom-right corner to start chatting in Singlish!</p>
            <div class="flex justify-center">
              <div class="animate-bounce bg-white bg-opacity-20 rounded-full p-3">
                <span class="text-3xl">👇</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="bg-white border-t border-gray-200 mt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div class="text-center text-gray-600">
            <p>&copy; 2025 Singlish Chatbot. Built with Nuxt 3, Vue 3, and Tailwind CSS.</p>
            <p class="mt-2 text-sm">Powered by fuzzy string matching for better Singlish understanding.</p>
          </div>
        </div>
      </footer>
    </div>

    <!-- Chatbot Widget -->
    <SinglishChatbot />
  </div>
</template>

<script setup>
// Page metadata
useHead({
  title: 'Singlish Chatbot - AI Chat Assistant',
  meta: [
    { name: 'description', content: 'Chat with our AI in Sri Lankan English (Singlish). Understands phrases like kohomada, oyage nama mokakda, and more!' },
    { name: 'keywords', content: 'singlish, chatbot, sri lanka, ai, chat, assistant' }
  ]
})
</script>

<style scoped>
.wave {
  animation-name: wave-animation;
  animation-duration: 2.5s;
  animation-iteration-count: infinite;
  transform-origin: 70% 70%;
  display: inline-block;
}

@keyframes wave-animation {
  0% { transform: rotate(0deg); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-8deg); }
  30% { transform: rotate(14deg); }
  40% { transform: rotate(-4deg); }
  50% { transform: rotate(10deg); }
  60% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); }
}

code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
