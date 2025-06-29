"""
AI-powered conceptual search for C.S. Lewis content.

This module provides semantic analysis capabilities to understand conceptual
queries and find relevant content in the caption database.
"""

import logging
import os
import json
from typing import List, Dict, Optional, Tuple
import re

# Optional AI API imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConceptAnalyzer:
    """Analyzes conceptual queries and generates semantic search strategies."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize AI clients if API keys are available
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logger.info("OpenAI client initialized")
            
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            logger.info("Anthropic client initialized")
    
    def get_available_models(self):
        """Get information about available AI models and analysis methods."""
        models = {
            'rule_based': {
                'name': 'Rule-Based Analysis',
                'description': 'Hand-crafted patterns for Lewis scholarship',
                'available': True,
                'speed': 'Very Fast',
                'accuracy': 'Good for specific patterns'
            }
        }
        
        if self.openai_client:
            models.update({
                'gpt-4': {
                    'name': 'GPT-4',
                    'description': 'Most capable model, best understanding',
                    'available': True,
                    'speed': 'Slower',
                    'accuracy': 'Excellent'
                },
                'gpt-4-turbo': {
                    'name': 'GPT-4 Turbo',
                    'description': 'Faster GPT-4 with good understanding',
                    'available': True,
                    'speed': 'Fast',
                    'accuracy': 'Excellent'
                },
                'gpt-3.5-turbo': {
                    'name': 'GPT-3.5 Turbo',
                    'description': 'Fast and cost-effective',
                    'available': True,
                    'speed': 'Very Fast',
                    'accuracy': 'Good'
                }
            })
        
        if self.anthropic_client:
            models.update({
                'claude-3-haiku': {
                    'name': 'Claude 3 Haiku',
                    'description': 'Fast and efficient',
                    'available': True,
                    'speed': 'Very Fast',
                    'accuracy': 'Good'
                },
                'claude-3-sonnet': {
                    'name': 'Claude 3 Sonnet',
                    'description': 'Balanced performance',
                    'available': True,
                    'speed': 'Fast',
                    'accuracy': 'Excellent'
                }
            })
        
        return models
    
    def analyze_concept_query(self, query: str, model: str = None) -> Dict:
        """
        Analyze a conceptual query and generate search strategies.
        
        Args:
            query: User's conceptual question or description
            model: Specific model to use (e.g., 'gpt-4', 'gpt-3.5-turbo', 'rule_based', or None for auto)
            
        Returns:
            Dict containing search terms, context, and strategy
        """
        logger.info(f"Analyzing concept query: {query} with model: {model}")
        
        # Use specific model if requested
        if model == 'rule_based':
            return self._analyze_with_rules(query)
        elif model and model.startswith('gpt-') and self.openai_client:
            return self._analyze_with_openai(query, model)
        elif model and model.startswith('claude-') and self.anthropic_client:
            return self._analyze_with_anthropic(query, model)
        else:
            # Auto-select: Try rule-based first (no cost), then fallback to AI if needed
            return self._smart_auto_analysis(query)
    
    def _smart_auto_analysis(self, query: str) -> Dict:
        """
        Smart auto-selection: Try rule-based first (free), then AI fallback if results are poor.
        
        Args:
            query: User's conceptual question or description
            
        Returns:
            Dict containing search terms, context, and strategy with fallback info
        """
        logger.info(f"Smart auto-analysis for query: {query}")
        
        # Step 1: Try rule-based analysis first (no cost)
        rule_analysis = self._analyze_with_rules(query)
        
        # Step 2: Check if rule-based analysis seems adequate
        if self._is_analysis_adequate(rule_analysis, query):
            # Rule-based analysis looks good, use it
            rule_analysis['auto_method'] = 'rule_based_primary'
            rule_analysis['explanation'] += ' (Auto: Rule-based analysis selected)'
            return rule_analysis
        
        # Step 3: Rule-based seems inadequate, try AI fallback
        logger.info("Rule-based analysis seems inadequate, trying AI fallback")
        
        # Try best available AI model
        if self.openai_client:
            ai_analysis = self._analyze_with_openai(query, 'gpt-4-turbo')
            ai_analysis['auto_method'] = 'ai_fallback'
            ai_analysis['explanation'] += ' (Auto: AI fallback used - rule-based seemed inadequate)'
            return ai_analysis
        elif self.anthropic_client:
            ai_analysis = self._analyze_with_anthropic(query, 'claude-3-sonnet')
            ai_analysis['auto_method'] = 'ai_fallback'
            ai_analysis['explanation'] += ' (Auto: AI fallback used - rule-based seemed inadequate)'
            return ai_analysis
        else:
            # No AI available, stick with rule-based
            rule_analysis['auto_method'] = 'rule_based_only'
            rule_analysis['explanation'] += ' (Auto: Rule-based only - no AI available)'
            return rule_analysis
    
    def _is_analysis_adequate(self, analysis: Dict, query: str) -> bool:
        """
        Determine if a rule-based analysis is adequate or if AI fallback is needed.
        
        Args:
            analysis: The rule-based analysis result
            query: Original query
            
        Returns:
            True if analysis seems adequate, False if AI fallback needed
        """
        query_lower = query.lower()
        search_terms = analysis.get('search_terms', [])
        
        # Criteria for adequate analysis:
        
        # 1. Has meaningful search terms (not just generic ones)
        if len(search_terms) < 3:
            logger.info("Analysis inadequate: Too few search terms")
            return False
        
        # 2. Contains specific objects/concepts when query implies them
        has_specific_objects = any(term in search_terms for term in [
            'microscope', 'books', 'fellowship', 'professor', 'teaching',
            'criticism', 'rejected', 'application', 'christmas'
        ])
        
        query_implies_objects = any(word in query_lower for word in [
            'object', 'thing', 'item', 'gift', 'present', 'criticism', 
            'feedback', 'professor', 'teaching', 'job', 'position'
        ])
        
        if query_implies_objects and not has_specific_objects:
            logger.info("Analysis inadequate: Query implies objects but none found in search terms")
            return False
        
        # 3. For very generic/abstract queries, prefer AI
        abstract_indicators = ['certain', 'something', 'some', 'particular', 'specific']
        if any(word in query_lower for word in abstract_indicators) and len(search_terms) < 5:
            logger.info("Analysis inadequate: Abstract query with few search terms")
            return False
        
        # 4. If query is very short and vague, try AI
        if len(query.split()) <= 4 and 'certain' in query_lower:
            logger.info("Analysis inadequate: Very short and vague query")
            return False
        
        # Analysis seems adequate
        logger.info(f"Analysis adequate: {len(search_terms)} search terms, specific objects: {has_specific_objects}")
        return True
    
    def _analyze_with_openai(self, query: str, model: str = "gpt-4-turbo") -> Dict:
        """Analyze query using OpenAI."""
        try:
            prompt = self._create_analysis_prompt(query)
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in C.S. Lewis scholarship and content analysis. Your task is to analyze conceptual queries about Lewis and generate effective search strategies."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = response.choices[0].message.content
            return self._parse_ai_response(result, f"openai-{model}")
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            return self._analyze_with_rules(query)
    
    def _analyze_with_anthropic(self, query: str, model: str = "claude-3-sonnet-20240229") -> Dict:
        """Analyze query using Anthropic Claude."""
        try:
            prompt = self._create_analysis_prompt(query)
            
            # Map model names to actual API model IDs
            model_map = {
                'claude-3-haiku': 'claude-3-haiku-20240307',
                'claude-3-sonnet': 'claude-3-sonnet-20240229'
            }
            api_model = model_map.get(model, model)
            
            response = self.anthropic_client.messages.create(
                model=api_model,
                max_tokens=800,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert in C.S. Lewis scholarship and content analysis. Your task is to analyze conceptual queries about Lewis and generate effective search strategies.\n\n{prompt}"
                    }
                ]
            )
            
            result = response.content[0].text
            return self._parse_ai_response(result, f"anthropic-{model}")
            
        except Exception as e:
            logger.error(f"Anthropic analysis failed: {e}")
            return self._analyze_with_rules(query)
    
    def _create_analysis_prompt(self, query: str) -> str:
        """Create the analysis prompt for AI models."""
        return f"""
You are analyzing a complex conceptual query about C.S. Lewis to find matching content in conversational transcripts discussing his letters, diaries, and biographical material.

QUERY: "{query}"

Your task is to generate multiple search strategies for finding nuanced, context-dependent scenarios and situations, not just keyword matches.

Please provide a JSON response with this enhanced structure:
{{
    "search_terms": ["specific_word1", "specific_word2", "specific_word3", "specific_word4", "specific_word5"],
    "contextual_phrases": ["exact phrase that might appear", "another specific phrase", "third contextual phrase"],
    "scenario_terms": ["situation_word1", "emotional_context1", "temporal_context1"],
    "psychological_terms": ["introspection", "self-doubt", "reflection", "considering"],
    "narrative_indicators": ["phrases that indicate storytelling about this scenario"],
    "related_concepts": ["concrete_concept1", "concrete_concept2"],
    "alternative_descriptions": ["how this scenario might be described differently"],
    "time_period": "approximate time period if relevant",
    "academic_context": "academic, personal, theological, literary, etc.",
    "confidence": "high/medium/low",
    "explanation": "detailed explanation of the multi-layered search strategy"
}}

ADVANCED GUIDELINES for Complex Scenarios:

1. SCENARIO UNDERSTANDING: If the query describes a situation or narrative, generate terms for:
   - The SITUATION (what is happening, what context or setting)
   - The EMOTIONS (feelings, mental states, reactions)
   - The ACTIONS (what Lewis is doing, thinking, or experiencing)
   - The CONTEXT (circumstances, relationships, timing, background)

2. PSYCHOLOGICAL CONTEXT: Include terms that capture internal mental states:
   - Self-reflection: "wondered", "questioned", "doubted", "considered"
   - Receiving feedback: "told", "advised", "criticized", "suggested"
   - Personal development: "needed to improve", "lacking", "weakness", "shortcoming"

3. NARRATIVE DETECTION: Look for words that indicate storytelling about past events:
   - "He was considering...", "Lewis thought about...", "He wondered if..."
   - "Someone told him...", "He received feedback that..."
   - "He reflected on...", "He was uncertain about..."

4. MULTIPLE SEARCH ANGLES: Generate different ways this scenario might be discussed:
   - Direct description of the situation
   - Emotional/psychological aspects
   - External feedback or interactions
   - Decision-making or thought processes
   - Specific context (academic, personal, theological, literary, etc.)

5. CONCRETE + ABSTRACT: Balance specific terms with situational context:
   - Concrete: specific objects, people, places, or events mentioned
   - Situational: "considering", "wondering", "uncertain", "reflection", "deciding"
   - Emotional: feelings and states like "worried", "excited", "doubtful", "confident"

EXAMPLES OF DIVERSE SCENARIO ANALYSIS:

Query: "Lewis considering a major decision and his doubts"
→ Search Terms: ["considering", "decision", "doubts", "uncertain", "weighing"]
→ Scenario Terms: ["wondering about", "thinking through", "contemplating"]
→ Psychological Terms: ["uncertainty", "hesitation", "reflection"]
→ Narrative Indicators: ["he was thinking", "Lewis wondered", "considering whether"]

Query: "Lewis received unexpected news about something"
→ Search Terms: ["received", "news", "told", "informed", "learned"]
→ Scenario Terms: ["found out", "was told that", "discovered"]
→ Narrative Indicators: ["someone told him", "he learned that", "came to know"]

Query: "Lewis had a meaningful conversation with someone"
→ Search Terms: ["conversation", "talked", "discussed", "spoke", "dialogue"]
→ Scenario Terms: ["deep discussion", "meaningful exchange", "important talk"]
→ Alternative Descriptions: ["heart-to-heart", "serious conversation", "frank discussion"]

Remember: You're searching for DISCUSSIONS about these scenarios in conversational transcripts, so include natural language patterns people use when recounting such situations.
"""
    
    def _parse_ai_response(self, response: str, source: str) -> Dict:
        """Parse AI response into structured format."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['search_terms', 'contextual_phrases', 'explanation']
                if all(field in parsed for field in required_fields):
                    parsed['source'] = source
                    parsed['method'] = 'ai_powered'
                    return parsed
            
            # If JSON parsing fails, extract information manually
            return self._extract_from_text(response, source)
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._analyze_with_rules(query)
    
    def _extract_from_text(self, text: str, source: str) -> Dict:
        """Extract search information from unstructured AI response."""
        # Simple extraction patterns
        search_terms = []
        
        # Look for quoted terms or lists
        quoted_terms = re.findall(r'"([^"]+)"', text)
        search_terms.extend(quoted_terms[:10])  # Limit to 10 terms
        
        return {
            'search_terms': search_terms if search_terms else ['Lewis', 'professor', 'criticism'],
            'contextual_phrases': ['academic development', 'professional growth'],
            'related_concepts': ['Oxford', 'Cambridge', 'teaching', 'scholarship'],
            'confidence': 'medium',
            'explanation': f'Extracted from {source} response',
            'source': source,
            'method': 'ai_extraction'
        }
    
    def _analyze_with_rules(self, query: str) -> Dict:
        """Fallback rule-based analysis when AI is not available."""
        logger.info("Using rule-based concept analysis")
        
        query_lower = query.lower()
        search_terms = []
        contextual_phrases = []
        related_concepts = []
        
        # Academic feedback and criticism scenarios - be very specific
        if any(term in query_lower for term in ['feedback', 'criticism', 'critique', 'weakness', 'improve', 'rejected', 'application', 'introspective']):
            if any(term in query_lower for term in ['professor', 'teaching', 'academic', 'fellowship', 'university', 'job']):
                # Specific external feedback about professional qualifications
                search_terms.extend(['rejected', 'turned down', 'unsuccessful', 'failed', 'denied'])
                search_terms.extend(['application', 'apply', 'applied', 'applying', 'candidate'])
                search_terms.extend(['fellowship', 'position', 'post', 'appointment', 'job'])
                search_terms.extend(['told', 'advised', 'suggested', 'recommended', 'informed'])
                search_terms.extend(['lacking', 'needed', 'required', 'must', 'should'])
                search_terms.extend(['committee', 'board', 'interviewer', 'examiner'])
                
                contextual_phrases.extend(['did not get', 'was not selected', 'application rejected'])
                contextual_phrases.extend(['told he needed', 'advised to improve', 'suggested he'])
                contextual_phrases.extend(['committee said', 'feedback was', 'criticism about'])
                contextual_phrases.extend(['not qualified', 'lacking experience', 'needed more'])
                
                related_concepts.extend(['Oxford', 'Cambridge', 'Magdalen', 'university'])
                related_concepts.extend(['interview', 'examination', 'selection', 'assessment'])
            else:
                # General external criticism/feedback (not personal growth)
                search_terms.extend(['told', 'said', 'advised', 'warned', 'criticized'])
                search_terms.extend(['fault', 'flaw', 'weakness', 'shortcoming', 'lacking'])
                contextual_phrases.extend(['told him', 'said he', 'criticized for'])
        
        # Career and professional development
        if any(term in query_lower for term in ['professor', 'teaching', 'academic', 'career', 'position']):
            search_terms.extend(['professor', 'teaching', 'lecturer', 'tutor'])
            search_terms.extend(['academic', 'university', 'college', 'fellowship'])
            contextual_phrases.extend(['academic career', 'teaching position', 'university appointment'])
            related_concepts.extend(['Oxford', 'Cambridge', 'Magdalen', 'English literature'])
        
        # Personal development and growth
        if any(term in query_lower for term in ['develop', 'improve', 'growth', 'better', 'change']):
            search_terms.extend(['develop', 'improve', 'growth', 'progress'])
            search_terms.extend(['change', 'better', 'advancement', 'development'])
            contextual_phrases.extend(['personal growth', 'self-improvement', 'character development'])
        
        # Christmas and gift scenarios
        if any(term in query_lower for term in ['christmas', 'gift', 'present', 'object']):
            search_terms.extend(['christmas', 'gift', 'present', 'object'])
            search_terms.extend(['microscope', 'books', 'instrument'])
            contextual_phrases.extend(['for christmas', 'christmas gift', 'christmas present'])
            if 'not have' in query_lower or 'will not' in query_lower or 'decided not' in query_lower:
                search_terms.extend(['not have', 'will not', 'decided not', 'won\'t get'])
                contextual_phrases.extend(['will not have', 'decided not to have', 'won\'t get'])

        # Relationships and social aspects
        if any(term in query_lower for term in ['father', 'family', 'friend', 'relationship']):
            search_terms.extend(['father', 'family', 'relationship', 'friend'])
            contextual_phrases.extend(['family relationship', 'personal relationship'])
        
        # Remove overly generic terms that cause noise
        generic_terms = ['Lewis', 'Jack', 'Clive', 'Staples']
        search_terms = [term for term in search_terms if term not in generic_terms]
        
        # If we have specific terms, don't add Lewis name (it's too broad)
        if not search_terms:
            search_terms = ['Lewis']
        
        # Remove duplicates and limit
        search_terms = list(set(search_terms))[:10]
        contextual_phrases = list(set(contextual_phrases))[:5]
        related_concepts = list(set(related_concepts))[:5]
        
        return {
            'search_terms': search_terms,
            'contextual_phrases': contextual_phrases,
            'related_concepts': related_concepts,
            'confidence': 'medium',
            'explanation': f'Identified as academic/professional query focusing on: {", ".join(search_terms[:3])}',
            'source': 'rules',
            'method': 'rule_based'
        }
    
    def generate_search_queries(self, analysis: Dict) -> List[str]:
        """Generate multiple search queries from enhanced concept analysis."""
        queries = []
        
        # Primary search with main terms
        if analysis.get('search_terms'):
            primary_terms = ' '.join(analysis['search_terms'][:3])
            queries.append(primary_terms)
        
        # Scenario-based searches (new)
        if analysis.get('scenario_terms'):
            scenario_query = ' '.join(analysis['scenario_terms'][:3])
            queries.append(scenario_query)
        
        # Psychological context searches (new)
        if analysis.get('psychological_terms'):
            psych_terms = ' '.join(analysis['psychological_terms'][:3])
            queries.append(psych_terms)
        
        # Contextual phrase searches
        for phrase in analysis.get('contextual_phrases', [])[:2]:
            queries.append(phrase)
        
        # Narrative indicator searches (new)
        for narrative in analysis.get('narrative_indicators', [])[:1]:
            queries.append(narrative)
        
        # Alternative description searches (new)
        for alt_desc in analysis.get('alternative_descriptions', [])[:1]:
            queries.append(alt_desc)
        
        # Combined concept searches
        if len(analysis.get('search_terms', [])) > 3:
            secondary_terms = ' '.join(analysis['search_terms'][3:6])
            queries.append(secondary_terms)
        
        # Related concept searches (reduced to make room for new approaches)
        for concept in analysis.get('related_concepts', [])[:1]:
            queries.append(concept)
        
        return queries[:8]  # Increased to 8 queries for more comprehensive search
    
    def rank_results(self, results: List[Dict], analysis: Dict, original_query: str) -> List[Dict]:
        """Rank search results based on conceptual relevance."""
        if not results:
            return results
        
        # Enhanced scoring based on term frequency, context, and semantic relevance
        scored_results = []
        
        search_terms = [term.lower() for term in analysis.get('search_terms', [])]
        contextual_phrases = [phrase.lower() for phrase in analysis.get('contextual_phrases', [])]
        original_query_lower = original_query.lower()
        
        # External feedback keywords (someone telling Lewis something)
        external_feedback_keywords = [
            'rejected', 'turned down', 'unsuccessful', 'failed', 'denied',
            'told', 'advised', 'suggested', 'recommended', 'informed', 'said',
            'committee', 'board', 'interviewer', 'examiner', 'selection',
            'application', 'apply', 'applied', 'applying', 'candidate',
            'not qualified', 'lacking', 'needed', 'required', 'must improve'
        ]
        
        # Generic terms that should be penalized (internal reflection, not external feedback)
        generic_penalty_terms = [
            'personal growth', 'self-improvement', 'development', 'evolving',
            'themes of', 'wrestling with', 'exploring', 'reflecting on'
        ]
        
        for result in results:
            score = 0
            text = result.get('text', '').lower()
            title = result.get('title', '').lower()
            
            # Higher weight for exact matches in original query terms
            query_words = original_query_lower.split()
            for word in query_words:
                if len(word) > 2:  # Ignore short words
                    if word in text:
                        score += 5
                    if word in title:
                        score += 3
            
            # Score based on search term matches
            for term in search_terms:
                if term in text:
                    score += 3
                if term in title:
                    score += 2
            
            # Score based on contextual phrase matches (high weight)
            for phrase in contextual_phrases:
                if phrase in text:
                    score += 8
                if phrase in title:
                    score += 5
            
            # Heavy penalty for generic "personal growth" content when looking for external feedback
            if any(keyword in original_query_lower for keyword in ['feedback', 'criticism', 'weakness', 'rejected', 'introspective']):
                # Heavily penalize generic internal reflection content
                generic_matches = sum(1 for term in generic_penalty_terms if term in text)
                if generic_matches > 0:
                    score -= generic_matches * 15  # Heavy penalty
                
                # Boost for actual external feedback indicators
                external_matches = sum(1 for keyword in external_feedback_keywords if keyword in text)
                if external_matches > 0:
                    score += external_matches * 10  # High reward for external feedback
                
                # Extra boost for specific rejection/application language
                if any(phrase in text for phrase in ['did not get', 'was not selected', 'application rejected', 'told he needed', 'advised to improve']):
                    score += 20
                
                # Boost results that mention specific academic contexts with external feedback
                if any(context in text for context in ['oxford', 'cambridge', 'magdalen', 'university', 'fellowship']) and external_matches > 0:
                    score += 10
            
            # Boost score for results with multiple relevant terms
            term_count = sum(1 for term in search_terms if term in text)
            if term_count > 1:
                score += term_count * 2
            
            # Penalize results that are too generic (biographical info or generic growth talk)
            generic_bio_terms = ['born', 'birth', 'family', 'staples', 'clive']
            bio_matches = len([term for term in generic_bio_terms if term in text])
            if bio_matches >= 2:
                score -= bio_matches * 3
            
            result['concept_score'] = score
            scored_results.append(result)
        
        # Sort by concept score, then by original search ranking
        scored_results.sort(key=lambda x: x.get('concept_score', 0), reverse=True)
        
        return scored_results