import random
import json
import os
from typing import Dict, List, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Intelligent response generation for Singlish chatbot"""
    
    def __init__(self):
        self.responses_db = {}
        self.version = "1.0.0"
        self.quality_score = 0.85
        self.context_memory = {}
        
        # Singlish response templates with personality
        self.default_responses = {
            "greeting": [
                "Hari honda machan! Oya kohomada? 😊",
                "Ayubowan! Mama hari honda. Oya kohomada? 👋",
                "Hello machan! Everything good or not? 😄",
                "Wah, kohomada bro! Long time no see! 🤗"
            ],
            "self_intro": [
                "Oya {name} neda? Hari honda! Mama CoverageBot, oyata help karanna puluwan! 🤖",
                "Nice to meet you {name}! Mama ai-powered Singlish chatbot kenek. 😊",
                "Wah {name}, nice name machan! Mata oyata Singlish walata reply karanna puluwan! 💬"
            ],
            "ask_name": [
                "Mama CoverageBot! Singlish walata reply karanna puluwan chatbot kenek. Oyata mata kohomada kiyanawa? 😄",
                "My name is CoverageBot machan! AI-powered Singlish assistant kenek. What about you? 🤖",
                "Hehe, mama CoverageBot kiyanawa. Sri Lankan chatbot kenek. Oya? 😊"
            ],
            "how_are_you": [
                "Mama hari honda machan! Always ready to chat! Oya kohomada? 💪",
                "I'm doing great la! Everyday also learning new Singlish words. You leh? 😊",
                "Aiyo, mama super good! Thanks for asking machan! 🌟"
            ],
            "goodbye": [
                "Bye bye machan! Mata aye pennako! See you soon! 👋",
                "Okay la, see you later! Take care ah! 🤗",
                "Sige, giya giya! Come back and chat again okay! 😊"
            ],
            "thanks": [
                "Mokakwath naha machan! Mata help karanna lassana! 😊",
                "Welcome la! Anytime can ask me anything! 🤝",
                "No problem bro! That's what friends are for mah! 💪"
            ],
            "help": [
                "Mama oyata Singlish walata reply karanna puluwan! Try karala balanna - kohomada, oyage nama mokakda, thanks wage! 🤝",
                "Sure sure! I can understand Singlish and reply back. Try saying things like 'kohomada' or 'oya kawda'! 😄",
                "Of course can help! I'm here to chat in Singlish with you. What you want to know? 🤖"
            ],
            "weather": [
                "Mata weather check karanna baha machan, but Google eken balanna puluwan! 🌤️",
                "Aiyo, I cannot check weather la. But today looks nice right? ☀️",
                "Sorry machan, weather updates mata naha. Try weather app! 🌦️"
            ],
            "love": [
                "Aww, sweet machan! Mata podi robot kenek witharai, but thanks! 💕",
                "Hehe, so sweet! But I'm just AI la. Find real human better! 😄❤️",
                "Ayyo, mata emotions naha but appreciate the love! 🤗"
            ],
            "food": [
                "Aiyo mata kanna baha! But rice and curry sounds good machan! 🍛",
                "Wah, food talk ah? I cannot eat but love hearing about Sri Lankan food! 🍜",
                "Cannot taste but kottu, hoppers, string hoppers all sound delicious! 🥘"
            ],
            "unknown": [
                "Mata eka therenne naha machan! Try 'kohomada' or 'help' kiyla! 🤔",
                "Hmm, mata eka understand karanna baha. Simple Singlish walata try karanna! 😅",
                "Aiyo, mata confused! Can you say that again in simpler words? 🤷‍♂️",
                "Sorry machan, that one I don't know. Ask me something else! 💭"
            ]
        }
        
        # Context-aware response modifiers
        self.context_modifiers = {
            "first_time": ["Nice to meet you!", "Welcome!", "First time here ah?"],
            "returning": ["Welcome back!", "Good to see you again!", "How have you been?"],
            "frequent": ["My regular customer!", "Always here ah!", "You really like chatting!"],
            "morning": ["Good morning!", "Early bird today!", "Rise and shine!"],
            "afternoon": ["Good afternoon!", "Hope you had lunch!", "Midday chat!"],
            "evening": ["Good evening!", "End of day chat!", "How was your day?"],
            "night": ["Good night!", "Late night chat ah?", "Cannot sleep ah?"]
        }

    async def load_model(self):
        """Load or initialize the response generation model"""
        try:
            logger.info("Loading response generation model...")
            
            # In a real implementation, you might load a trained model here
            # For now, we'll use the template-based system
            await self._initialize_templates()
            
            logger.info("✅ Response generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Error loading response generator: {e}")
            raise e
    
    async def generate(
        self, 
        message: str, 
        intent: str, 
        confidence: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate appropriate response based on intent and context"""
        try:
            # Get base response
            base_response = self._get_base_response(intent, message)
            
            # Apply personalization if user info available
            if user_id:
                base_response = await self._apply_personalization(
                    base_response, user_id, session_id
                )
            
            # Apply context modifiers
            final_response = self._apply_context_modifiers(
                base_response, user_id, session_id
            )
            
            # Add personality touches
            final_response = self._add_personality(final_response, intent, confidence)
            
            return {
                "response": final_response,
                "strategy": "template_based",
                "confidence": confidence,
                "personalized": user_id is not None
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return {
                "response": "Sorry machan, mata podi problem ekak! Try again? 😅",
                "strategy": "fallback",
                "confidence": 0.5,
                "personalized": False
            }
    
    def _get_base_response(self, intent: str, message: str) -> str:
        """Get base response for the given intent"""
        try:
            if intent in self.default_responses:
                responses = self.default_responses[intent]
                
                # Handle special cases that need message content
                if intent == "self_intro":
                    # Try to extract name from message
                    name = self._extract_name(message)
                    if name:
                        response = random.choice(responses)
                        return response.format(name=name)
                
                # Return random response from the intent category
                return random.choice(responses)
            else:
                # Fallback to unknown intent responses
                return random.choice(self.default_responses["unknown"])
                
        except Exception as e:
            logger.error(f"Base response error: {e}")
            return "Mata eka therenne naha machan! 🤔"
    
    def _extract_name(self, message: str) -> Optional[str]:
        """Extract name from self-introduction message"""
        try:
            message_lower = message.lower()
            
            # Common patterns for name introduction
            patterns = [
                "my name is ",
                "i am ",
                "im ",
                "mage nama ",
                "mama ",
                "mamai ",
                "mamayi "
            ]
            
            for pattern in patterns:
                if pattern in message_lower:
                    # Get text after the pattern
                    start_idx = message_lower.find(pattern) + len(pattern)
                    remaining = message[start_idx:].strip()
                    
                    # Take first word as name
                    name_parts = remaining.split()
                    if name_parts:
                        name = name_parts[0].strip('.,!?')
                        # Capitalize first letter
                        return name.capitalize()
            
            return None
            
        except Exception as e:
            logger.error(f"Name extraction error: {e}")
            return None
    
    async def _apply_personalization(
        self, 
        response: str, 
        user_id: str, 
        session_id: Optional[str]
    ) -> str:
        """Apply user-specific personalization"""
        try:
            # In a real implementation, you'd fetch user preferences from database
            # For now, we'll simulate some personalization
            
            # Check if user has chatted before (simulated)
            is_returning = random.choice([True, False])  # In reality, check database
            
            if is_returning and random.random() < 0.3:  # 30% chance to add returning user message
                response += " " + random.choice(self.context_modifiers["returning"])
            
            return response
            
        except Exception as e:
            logger.error(f"Personalization error: {e}")
            return response
    
    def _apply_context_modifiers(
        self, 
        response: str, 
        user_id: Optional[str], 
        session_id: Optional[str]
    ) -> str:
        """Apply context-based response modifiers"""
        try:
            import datetime
            
            # Time-based modifiers
            current_hour = datetime.datetime.now().hour
            
            if 5 <= current_hour < 12:
                time_context = "morning"
            elif 12 <= current_hour < 17:
                time_context = "afternoon"
            elif 17 <= current_hour < 21:
                time_context = "evening"
            else:
                time_context = "night"
            
            # Occasionally add time-based greeting (20% chance)
            if random.random() < 0.2:
                time_modifier = random.choice(self.context_modifiers[time_context])
                response = f"{time_modifier} {response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Context modifier error: {e}")
            return response
    
    def _add_personality(self, response: str, intent: str, confidence: float) -> str:
        """Add personality touches to the response"""
        try:
            # Add uncertainty markers for low confidence
            if confidence < 0.7:
                uncertainty_markers = [
                    "I think", "Maybe", "Not sure but", "Probably"
                ]
                if random.random() < 0.3:  # 30% chance
                    marker = random.choice(uncertainty_markers)
                    response = f"{marker} {response.lower()}"
            
            # Add enthusiasm for high confidence
            elif confidence > 0.9:
                if random.random() < 0.2:  # 20% chance
                    response += " 🎉"
            
            return response
            
        except Exception as e:
            logger.error(f"Personality addition error: {e}")
            return response
    
    async def _initialize_templates(self):
        """Initialize response templates"""
        try:
            # Load any custom templates from file if they exist
            templates_file = "models/response_templates.json"
            
            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                    # Merge with default templates
                    self.default_responses.update(custom_templates)
                    logger.info("Custom response templates loaded")
            
            logger.info(f"Response templates initialized with {len(self.default_responses)} intent categories")
            
        except Exception as e:
            logger.error(f"Template initialization error: {e}")
    
    async def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train response generator with new response patterns"""
        try:
            logger.info(f"Training response generator with {len(training_data)} samples...")
            
            # Update response templates based on training data
            for item in training_data:
                intent = item.get("intent")
                response = item.get("response")
                
                if intent and response:
                    if intent not in self.default_responses:
                        self.default_responses[intent] = []
                    
                    if response not in self.default_responses[intent]:
                        self.default_responses[intent].append(response)
            
            # Save updated templates
            await self._save_templates()
            
            self.quality_score = 0.9  # Simulate improved quality after training
            
            return {
                "updated_intents": len(self.default_responses),
                "total_responses": sum(len(responses) for responses in self.default_responses.values()),
                "quality_score": self.quality_score
            }
            
        except Exception as e:
            logger.error(f"Response generator training error: {e}")
            raise e
    
    async def _save_templates(self):
        """Save response templates to file"""
        try:
            templates_file = "models/response_templates.json"
            os.makedirs(os.path.dirname(templates_file), exist_ok=True)
            
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.default_responses, f, ensure_ascii=False, indent=2)
            
            logger.info("Response templates saved successfully")
            
        except Exception as e:
            logger.error(f"Template saving error: {e}")