export const chatbotIntents = [
  {
    intent: "greeting",
    phrases: [
      "kohomada", "kohomadha", "kohomda", "kohoma hari", "kohomada bro", 
      "machan kohomada", "ayubowan", "hello", "hi", "helo", "kohomada machan",
      "kohoma", "kohomada yako", "kohomada nangi", "kohomada akka"
    ],
    response: "Hari honda machan! Oya kohomada? 😊"
  },
  {
    intent: "self_intro",
    phrases: [
      "mage nama", "mage nama susith", "mamayi susith", "mamai susith",
      "mama susith", "my name is", "im susith", "i am susith",
      "mage nama mokakda", "mama susith kiyanne"
    ],
    response: "Oya susith neda? Hari honda! Mama CoverageBot, oyata help karanna puluwan! 🤖"
  },
  {
    intent: "ask_name",
    phrases: [
      "oyage nama mokakda", "oya kawda", "mokakda oyage nama",
      "whats your name", "who are you", "oyage nama",
      "oya mokakda", "oya kohomada kiyanne"
    ],
    response: "Mama CoverageBot! Singlish walata reply karanna puluwan chatbot kenek. Oyata mata kohomada kiyanawa? 😄"
  },
  {
    intent: "how_are_you",
    phrases: [
      "oya kohomada", "kohomada oya", "oyage hal", "how are you",
      "oya hari honda neda", "oyage weda mokakda", "oya hondaida"
    ],
    response: "Mama hari honda machan! Always ready to chat! Oya kohomada? 💪"
  },
  {
    intent: "goodbye",
    phrases: [
      "bye", "goodbye", "giya", "mata yanna ona", "api mathakai",
      "see you", "catch you later", "mama giyanne", "bye bye"
    ],
    response: "Bye bye machan! Mata aye pennako! See you soon! 👋"
  },
  {
    intent: "thanks",
    phrases: [
      "thanks", "thank you", "stuti", "stutiyi", "bohoma stuti",
      "thanks machan", "thank you nangi", "arigato"
    ],
    response: "Mokakwath naha machan! Mata help karanna lassana! 😊"
  },
  {
    intent: "help",
    phrases: [
      "help", "help karanna", "mata help karanna", "mokak karanne",
      "help me", "mata kiyala denna", "mokakda karanne"
    ],
    response: "Mama oyata Singlish walata reply karanna puluwan! Try karala balanna - kohomada, oyage nama mokakda, thanks wage! 🤝"
  },
  {
    intent: "weather",
    phrases: [
      "weather mokakda", "hawa mokakda", "rain enawada",
      "weather eka", "aye hawa", "weather check"
    ],
    response: "Mata weather check karanna baha machan, but Google eken balanna puluwan! 🌤️"
  },
  {
    intent: "love",
    phrases: [
      "mama oyata adare", "love you", "darling", "priya", "adare",
      "i love you", "oyata adare machan"
    ],
    response: "Aww, sweet machan! Mata podi robot kenek witharai, but thanks! 💕"
  },
  {
    intent: "food",
    phrases: [
      "kanna", "bath", "rice", "curry", "food", "kema",
      "bath kanna", "mokakda kanne", "lunch", "dinner"
    ],
    response: "Aiyo mata kanna baha! But rice and curry sounds good machan! 🍛"
  }
];