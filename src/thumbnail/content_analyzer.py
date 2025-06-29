"""Content analysis system for extracting engaging titles from C.S. Lewis texts."""

import logging
import re
import pytesseract
from PIL import Image
from typing import Optional, Dict, Any, List
from ..config.settings import settings


logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes C.S. Lewis content to generate engaging thumbnail titles."""
    
    def __init__(self, ai_provider: str = "openai"):
        self.ai_provider = ai_provider
        self.ai_client = None
        self._initialize_ai_client()
        
        # Common C.S. Lewis themes and patterns for title generation
        self.lewis_themes = {
            "theology": ["faith", "belief", "God", "Christianity", "divine", "prayer", "worship"],
            "literature": ["story", "narrative", "myth", "fairy tale", "allegory", "poetry"],
            "philosophy": ["reason", "logic", "truth", "reality", "existence", "knowledge"],
            "education": ["university", "Oxford", "Cambridge", "student", "learning", "teaching"],
            "friendship": ["friend", "companion", "fellowship", "Inklings", "Tolkien", "Barfield"],
            "personal": ["diary", "letter", "reflection", "memory", "experience", "feeling"]
        }
        
        # Year extraction patterns
        self.year_patterns = [
            r'\b(19\d{2})\b',  # 1900-1999
            r'\b(20\d{2})\b',  # 2000-2099
            r'in (\d{4})',     # "in 1924"
            r'during (\d{4})', # "during 1924"
            r'(\d{4}) was',    # "1924 was"
        ]
    
    def _initialize_ai_client(self):
        """Initialize AI client for content analysis."""
        try:
            if self.ai_provider == "openai":
                import openai
                # API key should be set via environment variable OPENAI_API_KEY
                self.ai_client = openai.OpenAI()
            elif self.ai_provider == "anthropic":
                import anthropic
                # API key should be set via environment variable ANTHROPIC_API_KEY
                self.ai_client = anthropic.Anthropic()
            
            logger.info(f"Initialized {self.ai_provider} client for content analysis")
            
        except Exception as e:
            logger.warning(f"Failed to initialize AI client: {e}")
            logger.info("Falling back to rule-based title generation")
            self.ai_client = None
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from book page image using OCR."""
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Use pytesseract to extract text
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            
            # Clean up the text
            cleaned_text = self._clean_ocr_text(extracted_text)
            
            logger.info(f"Extracted {len(cleaned_text)} characters from image")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from image {image_path}: {e}")
            return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean up OCR text by removing artifacts and improving readability."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)
        
        # Fix common OCR mistakes
        replacements = {
            'rn': 'm',
            'cl': 'd',
            '0': 'o',  # when clearly meant to be letter
            '1': 'l',  # when clearly meant to be letter
        }
        
        for old, new in replacements.items():
            # Only replace in word contexts
            text = re.sub(rf'\b{old}\b', new, text)
        
        return text.strip()
    
    def extract_year_from_content(self, content: str) -> Optional[str]:
        """Extract year from content using pattern matching."""
        for pattern in self.year_patterns:
            matches = re.findall(pattern, content)
            if matches:
                year = matches[0]
                # Validate year is reasonable for C.S. Lewis (1898-1963)
                if 1898 <= int(year) <= 1970:
                    logger.info(f"Extracted year from content: {year}")
                    return year
        
        logger.info("No year found in content")
        return None
    
    def generate_engaging_title(self, content: str, year: Optional[str] = None) -> str:
        """Generate an engaging thumbnail title from content."""
        if self.ai_client and self.ai_provider == "openai":
            return self._generate_title_with_openai(content, year)
        elif self.ai_client and self.ai_provider == "anthropic":
            return self._generate_title_with_anthropic(content, year)
        else:
            return self._generate_title_rule_based(content, year)
    
    def _generate_title_with_openai(self, content: str, year: Optional[str] = None) -> str:
        """Generate title using OpenAI GPT."""
        try:
            year_context = f" (from {year})" if year else ""
            
            prompt = f"""
            Create a short, engaging YouTube thumbnail title for a C.S. Lewis reading session.
            The title should be 3-8 words, capture the essence of the content, and sound intriguing.
            
            Examples of good titles:
            - "Lewis Laughs at a Dad Joke"
            - "Lewis Has a Bout with Bacon"
            - "Lewis Gives Tom Jones a Positive Review"
            - "Lewis Discusses University Life"
            - "Lewis Reflects on Medieval Literature"
            
            Content{year_context}:
            {content[:1000]}
            
            Generate ONE engaging title (3-8 words):
            """
            
            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            
            title = response.choices[0].message.content.strip()
            # Remove quotes if present
            title = title.strip('"\'')
            
            logger.info(f"Generated AI title: {title}")
            return title
            
        except Exception as e:
            logger.error(f"OpenAI title generation failed: {e}")
            return self._generate_title_rule_based(content, year)
    
    def _generate_title_with_anthropic(self, content: str, year: Optional[str] = None) -> str:
        """Generate title using Anthropic Claude."""
        try:
            year_context = f" (from {year})" if year else ""
            
            prompt = f"""
            Create a short, engaging YouTube thumbnail title for a C.S. Lewis reading session.
            The title should be 3-8 words, capture the essence of the content, and sound intriguing.
            
            Examples of good titles:
            - "Lewis Laughs at a Dad Joke"
            - "Lewis Has a Bout with Bacon"  
            - "Lewis Gives Tom Jones a Positive Review"
            - "Lewis Discusses University Life"
            - "Lewis Reflects on Medieval Literature"
            
            Content{year_context}:
            {content[:1000]}
            
            Generate ONE engaging title (3-8 words):
            """
            
            response = self.ai_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            title = response.content[0].text.strip()
            # Remove quotes if present
            title = title.strip('"\'')
            
            logger.info(f"Generated AI title: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Anthropic title generation failed: {e}")
            return self._generate_title_rule_based(content, year)
    
    def _generate_title_rule_based(self, content: str, year: Optional[str] = None) -> str:
        """Generate title using rule-based approach."""
        # Extract key phrases and themes
        content_lower = content.lower()
        
        # Look for specific topics or themes
        title_parts = ["Lewis"]
        
        # Check for specific actions or verbs
        actions = {
            "laugh": "Laughs",
            "smile": "Smiles", 
            "discuss": "Discusses",
            "reflect": "Reflects on",
            "write": "Writes About",
            "read": "Reads",
            "consider": "Considers",
            "think": "Thinks About",
            "remember": "Remembers",
            "critique": "Critiques",
            "praise": "Praises",
            "review": "Reviews"
        }
        
        found_action = None
        for action, title_action in actions.items():
            if action in content_lower:
                found_action = title_action
                break
        
        if not found_action:
            found_action = "Discusses"
        
        title_parts.append(found_action)
        
        # Extract topic/subject
        topics = {
            "university": "University Life",
            "oxford": "Oxford Days", 
            "cambridge": "Cambridge",
            "student": "Student Life",
            "friend": "Friendship",
            "tolkien": "Tolkien",
            "book": "Literature",
            "story": "Storytelling",
            "myth": "Mythology",
            "religion": "Faith",
            "god": "Divine Matters",
            "prayer": "Prayer",
            "war": "The War",
            "love": "Love",
            "marriage": "Marriage",
            "death": "Mortality",
            "pain": "Suffering",
            "joy": "Joy",
            "hope": "Hope"
        }
        
        found_topic = None
        for topic, title_topic in topics.items():
            if topic in content_lower:
                found_topic = title_topic
                break
        
        if found_topic:
            title_parts.append(found_topic)
        else:
            # Extract a key noun or phrase from content
            words = content.split()[:50]  # First 50 words
            important_words = [w for w in words if len(w) > 5 and w.isalpha()]
            if important_words:
                title_parts.append(important_words[0].title())
            else:
                title_parts.append("Life Insights")
        
        title = " ".join(title_parts)
        logger.info(f"Generated rule-based title: {title}")
        return title
    
    def analyze_content(self, content: str, year: Optional[str] = None) -> Dict[str, Any]:
        """Perform complete content analysis for thumbnail generation."""
        # Extract year if not provided
        extracted_year = year or self.extract_year_from_content(content)
        
        # Generate engaging title
        title = self.generate_engaging_title(content, extracted_year)
        
        # Identify themes
        themes = self._identify_themes(content)
        
        # Extract key quotes (first complete sentence up to 100 chars)
        key_quote = self._extract_key_quote(content)
        
        return {
            "title": title,
            "year": extracted_year or "Unknown",
            "themes": themes,
            "key_quote": key_quote,
            "content_length": len(content),
            "analysis_method": "ai" if self.ai_client else "rule-based"
        }
    
    def _identify_themes(self, content: str) -> List[str]:
        """Identify themes present in the content."""
        content_lower = content.lower()
        found_themes = []
        
        for theme, keywords in self.lewis_themes.items():
            if any(keyword in content_lower for keyword in keywords):
                found_themes.append(theme)
        
        return found_themes
    
    def _extract_key_quote(self, content: str) -> str:
        """Extract a key quote from the content."""
        # Find first complete sentence
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 100:  # Good length for a quote
                return sentence + "."
        
        # Fallback: return first 100 characters
        return content[:100] + "..." if len(content) > 100 else content