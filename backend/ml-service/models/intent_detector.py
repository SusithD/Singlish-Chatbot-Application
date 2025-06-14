import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sentence_transformers import SentenceTransformer
import pickle
import os
import json
from typing import Dict, List, Any, Tuple
import logging
from fuzzywuzzy import fuzz, process
import asyncio

logger = logging.getLogger(__name__)

class IntentDetector:
    """Advanced intent detection for Singlish chatbot"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.sentence_transformer = None
        self.intent_labels = []
        self.intent_data = {}
        self.version = "1.0.0"
        self.last_accuracy = 0.0
        self.model_path = "models/intent_detector.pkl"
        self.vectorizer_path = "models/intent_vectorizer.pkl"
        self.labels_path = "models/intent_labels.json"
        
        # Ensure models directory exists
        os.makedirs("models", exist_ok=True)
        
    async def load_model(self):
        """Load or initialize the intent detection model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                # Load existing model
                logger.info("Loading existing intent detection model...")
                
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                with open(self.labels_path, 'r') as f:
                    self.intent_labels = json.load(f)
                
                logger.info(f"✅ Intent model loaded successfully with {len(self.intent_labels)} intents")
                
            else:
                # Train new model with default data
                logger.info("No existing model found. Training new intent detection model...")
                await self._train_default_model()
                
            # Load sentence transformer for semantic similarity
            logger.info("Loading sentence transformer...")
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
        except Exception as e:
            logger.error(f"Error loading intent model: {e}")
            # Fallback to rule-based detection
            await self._initialize_fallback()
    
    async def predict(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict intent for given text"""
        try:
            if self.model and self.vectorizer:
                # Use ML model
                return await self._ml_predict(text, context)
            else:
                # Use rule-based fallback
                return await self._rule_based_predict(text, context)
                
        except Exception as e:
            logger.error(f"Error in intent prediction: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "alternatives": []
            }
    
    async def _ml_predict(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """ML-based intent prediction"""
        try:
            # Vectorize input
            text_vector = self.vectorizer.transform([text])
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(text_vector)[0]
            predicted_idx = np.argmax(probabilities)
            confidence = probabilities[predicted_idx]
            
            predicted_intent = self.intent_labels[predicted_idx]
            
            # Get alternative predictions
            alternatives = []
            for i, prob in enumerate(probabilities):
                if i != predicted_idx and prob > 0.1:  # Threshold for alternatives
                    alternatives.append({
                        "intent": self.intent_labels[i],
                        "confidence": float(prob)
                    })
            
            # Sort alternatives by confidence
            alternatives.sort(key=lambda x: x["confidence"], reverse=True)
            alternatives = alternatives[:3]  # Top 3 alternatives
            
            # Apply context-based adjustments if available
            if context:
                predicted_intent, confidence = self._apply_context(
                    predicted_intent, confidence, context
                )
            
            return {
                "intent": predicted_intent,
                "confidence": float(confidence),
                "alternatives": alternatives
            }
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return await self._rule_based_predict(text, context)
    
    async def _rule_based_predict(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Rule-based intent prediction (fallback)"""
        try:
            # Load default intents from frontend data
            intents_data = await self._load_default_intents()
            
            best_match = None
            best_score = 0.0
            alternatives = []
            
            for intent in intents_data:
                for phrase in intent["phrases"]:
                    # Use fuzzy matching
                    score = fuzz.ratio(text.lower(), phrase.lower()) / 100.0
                    
                    if score > best_score:
                        if best_match:
                            alternatives.append({
                                "intent": best_match["intent"],
                                "confidence": best_score
                            })
                        best_match = intent
                        best_score = score
                    elif score > 0.5:
                        alternatives.append({
                            "intent": intent["intent"],
                            "confidence": score
                        })
            
            if best_match and best_score > 0.6:
                # Sort and limit alternatives
                alternatives.sort(key=lambda x: x["confidence"], reverse=True)
                alternatives = alternatives[:3]
                
                return {
                    "intent": best_match["intent"],
                    "confidence": best_score,
                    "alternatives": alternatives
                }
            else:
                return {
                    "intent": "unknown",
                    "confidence": 0.0,
                    "alternatives": []
                }
                
        except Exception as e:
            logger.error(f"Rule-based prediction error: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "alternatives": []
            }
    
    async def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the intent detection model with new data"""
        try:
            logger.info(f"Training intent model with {len(training_data)} samples...")
            
            # Prepare training data
            texts = []
            labels = []
            
            for item in training_data:
                texts.append(item["text"])
                labels.append(item["intent"])
            
            # Create unique intent labels
            self.intent_labels = list(set(labels))
            
            # Convert labels to indices
            label_to_idx = {label: idx for idx, label in enumerate(self.intent_labels)}
            y = [label_to_idx[label] for label in labels]
            
            # Vectorize texts
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            X = self.vectorizer.fit_transform(texts)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            self.last_accuracy = accuracy
            
            # Save model
            await self._save_model()
            
            logger.info(f"✅ Model trained successfully! Accuracy: {accuracy:.3f}")
            
            return {
                "accuracy": accuracy,
                "num_intents": len(self.intent_labels),
                "training_samples": len(training_data),
                "model_version": self.version
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            raise e
    
    async def _train_default_model(self):
        """Train model with default Singlish intents"""
        try:
            # Load default intents
            intents_data = await self._load_default_intents()
            
            # Generate training data
            training_data = []
            for intent in intents_data:
                for phrase in intent["phrases"]:
                    training_data.append({
                        "text": phrase,
                        "intent": intent["intent"]
                    })
            
            # Train model
            await self.train(training_data)
            
        except Exception as e:
            logger.error(f"Default training error: {e}")
            await self._initialize_fallback()
    
    async def _load_default_intents(self) -> List[Dict[str, Any]]:
        """Load default intents from the frontend data"""
        try:
            # This would typically load from your chatbotIntents.js file
            # For now, we'll define some basic intents
            return [
                {
                    "intent": "greeting",
                    "phrases": [
                        "kohomada", "kohomadha", "kohomda", "hello", "hi",
                        "machan kohomada", "ayubowan", "kohoma hari"
                    ]
                },
                {
                    "intent": "self_intro",
                    "phrases": [
                        "mage nama", "my name is", "im", "i am",
                        "mama", "mamai", "mamayi"
                    ]
                },
                {
                    "intent": "ask_name",
                    "phrases": [
                        "oyage nama mokakda", "whats your name", "who are you",
                        "oya kawda", "oyage nama"
                    ]
                },
                {
                    "intent": "how_are_you",
                    "phrases": [
                        "oya kohomada", "how are you", "oyage hal",
                        "oya hari honda neda", "oya hondaida"
                    ]
                },
                {
                    "intent": "goodbye",
                    "phrases": [
                        "bye", "goodbye", "giya", "mata yanna ona",
                        "see you", "catch you later"
                    ]
                },
                {
                    "intent": "thanks",
                    "phrases": [
                        "thanks", "thank you", "stuti", "stutiyi",
                        "bohoma stuti", "thanks machan"
                    ]
                },
                {
                    "intent": "help",
                    "phrases": [
                        "help", "help karanna", "mata help karanna",
                        "help me", "mokak karanne"
                    ]
                }
            ]
            
        except Exception as e:
            logger.error(f"Error loading default intents: {e}")
            return []
    
    async def _save_model(self):
        """Save the trained model"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            with open(self.labels_path, 'w') as f:
                json.dump(self.intent_labels, f)
                
            logger.info("✅ Model saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    async def _initialize_fallback(self):
        """Initialize fallback rule-based system"""
        logger.info("Initializing fallback rule-based intent detection...")
        self.intent_labels = [
            "greeting", "self_intro", "ask_name", "how_are_you",
            "goodbye", "thanks", "help", "unknown"
        ]
    
    def _apply_context(self, intent: str, confidence: float, context: Dict[str, Any]) -> Tuple[str, float]:
        """Apply context to adjust intent prediction"""
        try:
            # Example context adjustments
            if context.get("previous_intent") == "greeting" and intent == "self_intro":
                confidence *= 1.2  # Boost confidence for natural conversation flow
            
            if context.get("user_id") and intent == "ask_name":
                confidence *= 0.8  # Lower confidence if user is already known
            
            # Ensure confidence doesn't exceed 1.0
            confidence = min(confidence, 1.0)
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"Context application error: {e}")
            return intent, confidence