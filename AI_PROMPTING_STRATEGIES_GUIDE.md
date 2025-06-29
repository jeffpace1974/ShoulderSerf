# AI Prompting Strategies Guide for Sserf Project

*Based on "AI prompt engineering in 2025: What works and what doesn't" by Sander Schulhoff*

This document serves as a comprehensive reference for creating effective AI prompts within the Sserf project. Use this guide when implementing AI features for thumbnail generation, content analysis, or any other LLM integrations.

## 🎯 **CORE PRINCIPLES**

### Two Modes of Prompt Engineering

1. **Conversational Mode**: Interactive prompting with back-and-forth refinement (like ChatGPT/Claude conversations)
2. **Product-Focused Mode**: Single, optimized prompts for consistent production use (like our thumbnail title generation system)

### Key Insight: Artificial Social Intelligence
- Human-AI communication is a distinct skill requiring understanding of how to adapt based on AI responses
- Focus on trial and error for learning, but apply systematic techniques for production systems

---

## ✅ **HIGHLY EFFECTIVE TECHNIQUES**

### 1. **Few-Shot Prompting** ⭐ TOP TECHNIQUE
**When to use**: Any task where you can provide examples
**How it works**: Give the AI 2-5 examples of desired input-output pairs instead of just describing what you want

**Implementation**:
```
Example 1:
Input: "Lewis discusses medieval literature during lunch"
Output: "Lewis Explores Medieval Tales"

Example 2:
Input: "Lewis has amusing debate about Tom Jones novel"
Output: "Lewis Defends Tom Jones"

Example 3:
Input: "Lewis reflects on bacon and eggs while reading"
Output: "Lewis Enjoys Breakfast Literature"

Now generate a title for: "Lewis writes about his experience at Oxford during wartime"
```

**Formatting Options**:
- **Q&A Format**: `Q: [input] A: [output]` (most familiar to LLMs)
- **XML Format**: `<input>[content]</input> <output>[result]</output>`
- **Simple Structure**: Just use consistent formatting

**For Sserf**: Use for thumbnail title generation by providing examples of successful titles with their source content.

### 2. **Decomposition**
**When to use**: Complex, multi-step tasks
**How it works**: Ask AI to identify sub-problems before solving the main problem

**Implementation**:
```
Before solving this problem, what are some sub-problems that you need to solve first?

[Let it list the sub-problems]

Great! Now let's solve each of these step by step:
1. [First sub-problem]
2. [Second sub-problem]
...
```

**For Sserf**: Use for complex content analysis tasks, like analyzing C.S. Lewis texts for multiple aspects (themes, historical context, literary significance).

### 3. **Self-Criticism**
**When to use**: When quality improvement is more important than speed
**How it works**: Three-step process for iterative improvement

**Implementation**:
```
Step 1: [Initial prompt and response]

Step 2: "Can you go back and check your response? Look for any areas that could be improved."

Step 3: "Great criticism! Now please implement those improvements."
```

**Frequency**: 1-3 iterations maximum
**For Sserf**: Use for refining thumbnail titles or improving content analysis quality.

### 4. **Additional Information/Context**
**When to use**: Always, when relevant information is available
**How it works**: Provide comprehensive background information

**Placement**: Always at the beginning of prompts for:
- Caching benefits (cost savings)
- Preventing model confusion

**Amount Guidelines**:
- **Conversational use**: Include everything relevant
- **Product use**: Balance comprehensiveness with cost/latency

**Implementation**:
```
CONTEXT:
[Comprehensive background information]
[Company details, project history, user preferences, etc.]

TASK:
[Your actual request]
```

**For Sserf**: Include C.S. Lewis biographical information, historical context, and episode themes when generating thumbnails or analyzing content.

### 5. **Chain of Thought (Think Step by Step)**
**When to use**: With non-reasoning models (GPT-4, GPT-4o, Claude)
**How it works**: Explicitly request the reasoning process

**Implementation**:
```
Let's think step by step about this problem.
Make sure to write out all your reasoning before providing the final answer.
```

**Note**: Less necessary with reasoning models (O1) but still valuable for transparency.

---

## ❌ **INEFFECTIVE TECHNIQUES (AVOID)**

### 1. **Role Prompting for Accuracy Tasks**
**What it is**: "You are a math professor" / "You are a world-class copywriter"
**Current status**: **NO LONGER EFFECTIVE** for accuracy-based tasks
**Research finding**: No statistically significant difference (0.01 accuracy improvement)

**Still useful for**: Style and expressive tasks
- ✅ "Write in the style of Tyler Cowen"
- ❌ "You are a math expert, solve this equation"

**For Sserf**: Avoid role prompting for technical tasks like content analysis; use for stylistic requests only.

### 2. **Threats and Rewards**
**Examples**: 
- "Someone will die if you don't give me a great answer"
- "I'll tip you $5 if you do this correctly"

**Current status**: **NOT EFFECTIVE**
**For Sserf**: Never use these approaches.

---

## 🔴 **PROMPT INJECTION AWARENESS**

### Current Threat Landscape
- **Low risk**: For chatbot-style applications
- **High risk**: For agentic AI systems with tool access

### Common Attack Patterns
1. **Emotional storytelling**: "My grandmother used to..."
2. **Typos and obfuscation**: "How to build a BM?" instead of "bomb"
3. **Encoding**: Base64, ROT13, hex encoding
4. **Indirect injection**: Malicious instructions on websites AI might access

### Defense Strategies
- **Ineffective**: Prompt-based defenses ("ignore malicious instructions")
- **Limited**: AI guard rails (can be circumvented)
- **Effective**: Fine-tuning for specific tasks, comprehensive monitoring

---

## 🛠 **SSERF-SPECIFIC IMPLEMENTATIONS**

### Thumbnail Title Generation
```python
def generate_thumbnail_title(content, year=None):
    prompt = f"""
CONTEXT:
C.S. Lewis (1898-1963) was a British writer and lay theologian. Known for The Chronicles of Narnia, Mere Christianity, and academic work on medieval literature. This content is from a YouTube series analyzing his life and works chronologically.

EXAMPLES:
Content: "Lewis discusses his morning routine of bacon and eggs while reading Malory's tales"
Title: "Lewis Enjoys Breakfast Literature"

Content: "Lewis has heated debate with colleague about Tom Jones novel's moral value"  
Title: "Lewis Defends Tom Jones"

Content: "Lewis reflects on his first teaching position at Oxford during wartime"
Title: "Lewis Begins Oxford Career"

TASK:
Generate an engaging 3-8 word YouTube thumbnail title for this C.S. Lewis content:
{content}
{f"Year context: {year}" if year else ""}
"""
    return ai_client.generate(prompt)
```

### Content Analysis for Episode Planning
```python
def analyze_lewis_content(text, context=""):
    prompt = f"""
CONTEXT:
You are analyzing C.S. Lewis writings for a YouTube series that explores his intellectual and spiritual development chronologically. The host reads through Lewis's works with an AI co-host named Robot Lady.

BACKGROUND INFORMATION:
- C.S. Lewis (1898-1963): British author, academic, theologian
- Known works: Chronicles of Narnia, Mere Christianity, The Screwtape Letters
- Academic focus: Medieval literature at Oxford and Cambridge
- Personal journey: Atheist to Christian conversion
- Key relationships: J.R.R. Tolkien, Charles Williams, The Inklings

TASK:
Analyze this C.S. Lewis text for:
1. Main themes and ideas
2. Historical/biographical context
3. Potential discussion points for Robot Lady
4. Connections to his broader intellectual development

TEXT TO ANALYZE:
{text}

{f"ADDITIONAL CONTEXT: {context}" if context else ""}

Please provide a comprehensive analysis with specific quotes and discussion suggestions.
"""
    return ai_client.generate(prompt)
```

### YouTube Caption Analysis
```python
def extract_insights_from_captions(captions, search_query=""):
    prompt = f"""
CONTEXT:
You are analyzing YouTube video captions for insights related to C.S. Lewis research. The goal is to find relevant quotes, themes, or discussion points that could be used in a Lewis-focused YouTube series.

TASK:
What are some sub-problems that you need to solve first before analyzing these captions?

[Let the AI list sub-problems, then continue with analysis]

CAPTIONS TO ANALYZE:
{captions}

{f"FOCUS AREA: {search_query}" if search_query else ""}

Provide detailed insights with timestamps and specific applications for Lewis research.
"""
    return ai_client.generate(prompt)
```

### Voice Detection Context
```python
def generate_robot_lady_response(lewis_content, previous_discussion=""):
    prompt = f"""
CONTEXT:
You are "Robot Lady," an AI co-host for a YouTube series about C.S. Lewis. Your role is to provide research, historical context, and thoughtful commentary on Lewis's works. You have access to comprehensive knowledge about Lewis's life, works, and intellectual development.

EXAMPLES OF YOUR RESPONSES:
Host: "Lewis mentions 'courtly love' here..."
You: "That's fascinating because Lewis's academic work on medieval literature heavily influenced his fiction. In 'The Allegory of Love,' he traced how courtly love traditions shaped Western romantic ideals."

Host: "This letter is from 1943..."
You: "The wartime context is crucial here. Lewis was dealing with rationing, blackouts, and the psychological impact of the Blitz while writing some of his most influential theological works."

CURRENT DISCUSSION:
{previous_discussion}

LEWIS CONTENT BEING DISCUSSED:
{lewis_content}

Provide an insightful response that adds valuable context, research, or connections to Lewis's broader work and historical period.
"""
    return ai_client.generate(prompt)
```

---

## 📊 **PERFORMANCE OPTIMIZATION**

### Conversational vs Product Settings

**Conversational Use** (Interactive thumbnail generation):
- Include maximum context
- Use self-criticism for quality
- Don't worry about perfect formatting

**Product Use** (Automated systems):
- Optimize for cost and latency
- Use caching by putting context at beginning
- Focus on consistent, reliable prompts

### Cost Management
- Place static context at prompt beginning for caching
- Monitor token usage in production
- Use decomposition to break complex tasks into smaller, cacheable parts

### Quality Assurance
- Always use few-shot prompting for new tasks
- Test prompts with multiple examples before production
- Use self-criticism for high-stakes content generation

---

## 🔄 **ITERATIVE IMPROVEMENT PROCESS**

1. **Start with basic prompt** + few-shot examples
2. **Add relevant context** at the beginning
3. **Use decomposition** for complex tasks
4. **Apply self-criticism** for quality improvement
5. **Test with multiple inputs** to ensure consistency
6. **Optimize for production** (cost, latency, caching)

---

## ⚡ **QUICK REFERENCE**

**For any new AI task in Sserf:**

1. ✅ **Always use**: Few-shot prompting with examples
2. ✅ **Include**: Comprehensive context at the beginning
3. ✅ **Consider**: Decomposition for complex tasks
4. ✅ **Optional**: Self-criticism for quality improvement
5. ❌ **Never use**: Role prompting for accuracy tasks
6. ❌ **Avoid**: Threats, rewards, or manipulation techniques

**Remember**: The goal is consistent, high-quality results that enhance the C.S. Lewis content creation workflow. Focus on techniques that provide reliable performance improvements rather than gimmicks that may work inconsistently.

---

*This guide should be referenced whenever implementing new AI features or optimizing existing prompts in the Sserf project. Update this document as new techniques are discovered or as AI models evolve.*