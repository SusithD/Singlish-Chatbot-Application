import numpy as np
from typing import Dict, List, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

class SinglishClassifier:
    """Singlish language detection and classification"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.last_accuracy = 0.85
        
        # Singlish language markers
        self.singlish_markers = {
            'particles': ['lah', 'lor', 'meh', 'sia', 'leh', 'hor', 'ah'],
            'sinhala_words': ['kohomada', 'mama', 'oya', 'nama', 'mokakda'],
            'grammar_patterns': ['got', 'never', 'already', 'still', 'also'],
            'expressions': ['aiyo', 'wah', 'shiok', 'steady', 'chio']
        }
    
    async def load_model(self):
        """Load the Singlish classification model"""
        try:
            logger.info("Loading Singlish classifier...")
            # Initialize classification rules
            await self._initialize_classifier()
            logger.info("✅ Singlish classifier loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Singlish classifier: {e}")
            raise e
    
    async def classify(self, text: str) -> Dict[str, Any]:
        """Classify text as Singlish or other languages"""
        try:
            text_lower = text.lower()
            
            # Calculate Singlish score
            singlish_score = self._calculate_singlish_score(text_lower)
            
            # Determine classification
            if singlish_score > 0.3:
                classification = "singlish"
                confidence = min(singlish_score, 1.0)
            elif self._contains_sinhala(text_lower):
                classification = "sinhala_romanized"
                confidence = 0.8
            else:
                classification = "english"
                confidence = 1.0 - singlish_score
            
            return {
                "classification": classification,
                "confidence": confidence,
                "singlish_score": singlish_score,
                "features": self._extract_features(text_lower)
            }
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "classification": "unknown",
                "confidence": 0.0,
                "singlish_score": 0.0,
                "features": {}
            }
    
    def _calculate_singlish_score(self, text: str) -> float:
        """Calculate how Singlish the text is"""
        words = text.split()
        if not words:
            return 0.0
        
        score = 0.0
        
        # Check for Singlish particles
        for particle in self.singlish_markers['particles']:
            if particle in text:
                score += 0.3
        
        # Check for Sinhala words
        for word in self.singlish_markers['sinhala_words']:
            if word in text:
                score += 0.4
        
        # Check for grammar patterns
        for pattern in self.singlish_markers['grammar_patterns']:
            if pattern in text:
                score += 0.2
        
        # Check for expressions
        for expr in self.singlish_markers['expressions']:
            if expr in text:
                score += 0.3
        
        return min(score, 1.0)
    
    def _contains_sinhala(self, text: str) -> bool:
        """Check if text contains romanized Sinhala"""
        sinhala_indicators = ['kohomada', 'oyage', 'mage', 'mama', 'oya']
        return any(indicator in text for indicator in sinhala_indicators)
    
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features"""
        return {
            'has_particles': any(p in text for p in self.singlish_markers['particles']),
            'has_sinhala': self._contains_sinhala(text),
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    async def _initialize_classifier(self):
        """Initialize the classification system"""
        logger.info("Singlish classifier initialized with rule-based approach")