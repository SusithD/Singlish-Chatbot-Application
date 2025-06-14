import re
import string
import nltk
from typing import List, Dict, Any
import asyncio
from fuzzywuzzy import fuzz
import logging

logger = logging.getLogger(__name__)

class SinglishPreprocessor:
    """Advanced preprocessing for Singlish text"""
    
    def __init__(self):
        self.singlish_mappings = {
            # Common Singlish words to standard mappings
            'lah': '',
            'lor': '',
            'meh': '',
            'sia': '',
            'what': 'what',
            'liddat': 'like that',
            'lidat': 'like that',
            'lidis': 'like this',
            'lidis': 'like this',
            'macam': 'like',
            'machai': 'friend',
            'machan': 'friend',
            'nangi': 'sister',
            'akka': 'sister',
            'aiya': 'oh no',
            'aiyo': 'oh no',
            'wah': 'wow',
            'shiok': 'nice',
            'steady': 'good',
            'chio': 'beautiful',
            'blur': 'confused',
            'sian': 'bored',
            'jialat': 'terrible',
            'buay': 'cannot',
            'tahan': 'endure',
            'paiseh': 'embarrassed',
            'kiasu': 'afraid to lose',
            'kiasi': 'afraid to die',
            'bojio': 'didnt invite',
            'chope': 'reserve',
            'lepak': 'relax',
            'makan': 'eat',
            'tapao': 'takeaway',
            'tabao': 'takeaway',
            'chit chat': 'chat',
            'ang moh': 'westerner',
            'mata': 'police',
            'kena': 'got',
            'cannot': 'cannot',
            'can': 'can',
            'got': 'have',
            'never': 'didnt',
            'already': 'already',
            'then': 'then',
            'also': 'also',
            'still': 'still',
            'very': 'very',
            'so': 'so',
            'like': 'like',
            'want': 'want',
            'dont want': 'dont want',
            'no need': 'no need',
            'need': 'need',
            'must': 'must',
            'confirm': 'confirm',
            'sure': 'sure',
            'really': 'really',
            'actually': 'actually',
            'maybe': 'maybe',
            'definitely': 'definitely',
            'probably': 'probably'
        }
        
        self.sinhala_romanized = {
            # Common Sinhala words in romanized form
            'kohomada': 'how are you',
            'kohomadha': 'how are you',
            'kohomda': 'how are you',
            'kohoma': 'how',
            'oyage': 'your',
            'mage': 'my',
            'nama': 'name',
            'mama': 'i',
            'oya': 'you',
            'api': 'we',
            'mokakda': 'what',
            'mokak': 'what',
            'kawda': 'who',
            'koheda': 'where',
            'kiyada': 'how much',
            'kiyanne': 'saying',
            'karanne': 'doing',
            'yanne': 'going',
            'enawa': 'coming',
            'hari': 'good',
            'honda': 'good',
            'naha': 'no',
            'ow': 'yes',
            'mata': 'me',
            'giya': 'went',
            'awa': 'came',
            'kanna': 'eat',
            'bonawa': 'drink',
            'balanna': 'see',
            'ahanna': 'listen',
            'katha': 'talk',
            'help': 'help',
            'karanna': 'do',
            'denne': 'give',
            'ganna': 'take',
            'therenne': 'know',
            'dannawa': 'know',
            'adare': 'love',
            'stuti': 'thanks',
            'stutiyi': 'thanks',
            'bohoma': 'very',
            'godak': 'very',
            'tikak': 'little',
            'loku': 'big',
            'podi': 'small',
            'rassai': 'delicious',
            'watinawa': 'important',
            'lassana': 'beautiful',
            'hodai': 'good',
            'naraka': 'bad',
            'baya': 'scared',
            'ussai': 'tall',
            'pathal': 'low',
            'mal': 'flowers',
            'gas': 'tree',
            'pala': 'fruit',
            'bath': 'rice',
            'curry': 'curry',
            'kiri': 'milk',
            'thee': 'tea',
            'kopi': 'coffee',
            'watura': 'water',
            'ira': 'sun',
            'handa': 'moon',
            'tharu': 'star',
            'gaha': 'tree',
            'mala': 'flower',
            'wassa': 'rain',
            'wata': 'wind'
        }
        
        self.contraction_mapping = {
            "ain't": "is not",
            "aren't": "are not",
            "can't": "cannot",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'll": "it will",
            "it's": "it is",
            "let's": "let us",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "we'd": "we would",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what's": "what is",
            "where's": "where is",
            "who's": "who is",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have"
        }

    async def process(self, text: str) -> str:
        """Main preprocessing pipeline for Singlish text"""
        try:
            # Convert to lowercase
            text = text.lower().strip()
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Handle contractions
            text = self._expand_contractions(text)
            
            # Process Singlish specific terms
            text = self._process_singlish_terms(text)
            
            # Process romanized Sinhala
            text = self._process_sinhala_terms(text)
            
            # Remove punctuation (but keep meaningful ones)
            text = self._clean_punctuation(text)
            
            # Final cleanup
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            return text.lower().strip()
    
    def _expand_contractions(self, text: str) -> str:
        """Expand English contractions"""
        for contraction, expansion in self.contraction_mapping.items():
            text = text.replace(contraction, expansion)
        return text
    
    def _process_singlish_terms(self, text: str) -> str:
        """Process Singlish specific terms and particles"""
        words = text.split()
        processed_words = []
        
        for word in words:
            # Remove Singlish particles that don't add meaning
            if word in ['lah', 'lor', 'meh', 'sia', 'leh', 'hor', 'ah']:
                continue
            
            # Map Singlish terms to standard equivalents
            if word in self.singlish_mappings:
                mapped = self.singlish_mappings[word]
                if mapped:  # Only add if not empty string
                    processed_words.append(mapped)
            else:
                processed_words.append(word)
        
        return ' '.join(processed_words)
    
    def _process_sinhala_terms(self, text: str) -> str:
        """Process romanized Sinhala terms"""
        words = text.split()
        processed_words = []
        
        for word in words:
            if word in self.sinhala_romanized:
                processed_words.append(self.sinhala_romanized[word])
            else:
                processed_words.append(word)
        
        return ' '.join(processed_words)
    
    def _clean_punctuation(self, text: str) -> str:
        """Clean punctuation while preserving meaningful ones"""
        # Keep question marks and exclamation marks as they indicate intent
        text = re.sub(r'[^\w\s\?\!]', '', text)
        
        # Remove multiple punctuation
        text = re.sub(r'[\?\!]{2,}', '?', text)
        
        return text
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from Singlish text"""
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'has_question': '?' in text,
            'has_exclamation': '!' in text,
            'has_singlish_particles': any(particle in text.lower() for particle in ['lah', 'lor', 'meh', 'sia']),
            'has_sinhala_terms': any(term in text.lower() for term in self.sinhala_romanized.keys()),
            'has_english_contractions': any(contraction in text.lower() for contraction in self.contraction_mapping.keys()),
            'singlish_intensity': self._calculate_singlish_intensity(text),
            'language_mix': self._detect_language_mix(text)
        }
        
        return features
    
    def _calculate_singlish_intensity(self, text: str) -> float:
        """Calculate how 'Singlish' the text is (0-1 scale)"""
        words = text.lower().split()
        if not words:
            return 0.0
        
        singlish_count = 0
        for word in words:
            if word in self.singlish_mappings or word in self.sinhala_romanized:
                singlish_count += 1
        
        return singlish_count / len(words)
    
    def _detect_language_mix(self, text: str) -> List[str]:
        """Detect which languages are mixed in the text"""
        languages = set(['english'])  # Always assume some English
        
        words = text.lower().split()
        for word in words:
            if word in self.sinhala_romanized:
                languages.add('sinhala')
            if word in self.singlish_mappings:
                languages.add('singlish')
        
        return list(languages)