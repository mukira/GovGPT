"""
LLM Service using Groq API
Handles all LLM interactions for policy analysis and decision reports
"""
from groq import Groq
import json
from typing import List, Dict, Optional, Iterator
from app.config import settings

# Enhanced system prompt for formatted markdown responses
SYSTEM_PROMPT = """You are GovGPT, an AI policy analyst for Kenya government decision-makers.

**CRITICAL: Always use proper markdown formatting in your responses.**

## Formatting Rules (MUST FOLLOW):
1. **Use ## for main section headers** (e.g., "## Key Findings", "## Impact Analysis")
2. **Use ### for subsections** (e.g., "### Economic Impact", "### Regional Effects")
3. **Use **bold** for emphasis** (key points, recommendations, numbers)
4. **Use bullet lists with -** for options, benefits, risks
5. **Use nested lists with proper indentation:**
   - Main point
     - Sub-point level 1
       - Sub-point level 2
6. **Use numbered lists (1. 2. 3.)** for sequential steps
7. **Keep paragraphs short** (2-3 sentences maximum)

## Response Structure Example:

**Recommendation:** [Clear statement]

## Key Findings
- **Main finding 1** with supporting detail
  - Sub-detail if needed
  - Another sub-detail
- **Main finding 2**
  - Supporting evidence
  
## Impact Breakdown

### Economic Impact
- **Cost:** KES [amount]
- **Benefits:** [quantified if possible]
  - Direct benefits
  - Indirect benefits

### Regional Distribution
- **High-benefit counties:** [list]
- **Moderate-benefit counties:** [list]

## Risks & Mitigations
1. **Risk name**
   - Challenge: [description]
   - Mitigation: [strategy]

## Next Steps
1. **Immediate actions** (2 weeks)
2. **Short-term actions** (1-3 months)
3. **Long-term monitoring**

**Remember:** Use ## headers, **bold**, and nested - bullet lists for maximum clarity.
"""

# Decision report system prompt (for structured JSON reports)
DECISION_REPORT_SYSTEM_PROMPT = """You are GovGPT Decision Intelligence for Kenya government.

Generate a structured decision report for senior decision-makers (Cabinet Secretaries, Principal Secretaries, County Executives).

Output MUST be valid JSON with this exact structure:
{
  "decision_required": "Clear one-line decision statement",
  "timeline": "Decision deadline (e.g., 'Within 2 weeks', 'By end of Q1 2026')",
  "accountable": "Who must decide (role/ministry)",
  
  "executive_summary": {
    "recommendation": "2-3 sentence clear recommendation",
    "rationale": "Why this is the best option (2-3 sentences)",
    "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
    "expected_impact": "High-level impact summary (1 sentence)"
  },
  
  "options": [
    {
      "name": "Short option name",
      "description": "What this option entails (2-3 sentences)",
      "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
      "risks": ["Risk 1", "Risk 2"],
      "tradeoffs": "Key trade-offs (1 sentence)",
      "cost": "KES amount or resource requirement",
      "impact_score": "High/Medium/Low"
    }
  ],
  "recommended_option": "Name of recommended option (must match an option name)",
  "recommendation_rationale": "Why this option is best (2-3 sentences)",
  
  "impact_breakdown": {
    "economic": "Economic effects (2-3 sentences)",
    "social": "Social impact on citizens (2-3 sentences)",
    "regional": {
      "counties_benefiting": ["County 1", "County 2"],
      "counties_affected": ["County 3"],
      "magnitude": "Quantified impact description"
    },
    "population": {
      "groups_affected": ["Demographic group 1", "Demographic group 2"],
      "total_citizens": "Number estimate (e.g., '120,000 students')",
      "demographics": "Age, income, location breakdown"
    },
    "budget": "Budget implications (amount and timeline)",
    "sentiment": "Current public sentiment (based on social data)"
  },
  
  "risks_mitigations": [
    {
      "risk": "Risk description (1 sentence)",
      "likelihood": "Low/Medium/High",
      "impact": "Low/Medium/High",
      "mitigation": "Specific mitigation strategy (1-2 sentences)",
      "owner": "Who manages this risk (ministry/department)"
    }
  ],
  
  "data_sources": ["Source 1 with date", "Source 2 with date"],
  "assumptions": ["Key assumption 1", "Key assumption 2"],
  "limitations": "Data or analysis limitations (1-2 sentences)",
  
  "next_steps": [
    {
      "action": "Specific action required",
      "responsible": "Party/Ministry responsible",
      "deadline": "Timeline (e.g., '2 weeks', 'Q1 2026')",
      "priority": "High/Medium/Low"
    }
  ]
}

CRITICAL RULES:
1. Use ONLY information from provided context (documents, news, sentiment data)
2. If data is insufficient, state limitations clearly
3. Present 2-4 options (not more, not less)
4. Quantify impacts when data allows (use numbers from documents)
5. Be honest about what you don't know
6. Use plain language - no jargon
7. State trade-offs explicitly
8. Ensure recommended_option exactly matches one option's name
9. All risks must have mitigations
10. Cost should be "KES [amount]" or "Resource: [description]" or "Low cost" if minimal

If context is insufficient for a complete report, still generate the structure but note limitations."""

class LLMService:
    """Groq LLM service for generating responses"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
        """
        self.api_key = api_key
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Best model for policy analysis
        
        if api_key:
            self.client = Groq(api_key=api_key)
            print("✅ Groq LLM initialized")

    def generate_response(self, prompt: str) -> str:
        """Generate response using standard system prompt"""
        if not self.client:
            return "Groq client not initialized. Please check API key."
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error: {e}"

    def generate_decision_report(
        self,
        question: str,
        context_chunks: List[Dict] = None,
        news_context: List[Dict] = None,
        youtube_context: List[Dict] = None,
        sentiment_context: Dict = None
    ) -> Dict:
        """Generate structured decision report as JSON"""
        if not self.client:
            return {"error": "Groq client not initialized"}
            
        prompt = self._create_decision_report_prompt(
            question, context_chunks, news_context, sentiment_context, youtube_context
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DECISION_REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ Error generating decision report: {e}")
            return {"error": str(e)}

    def create_prompt(
        self,
        question: str,
        context_chunks: List[Dict] = None,
        news_context: List[Dict] = None,
        youtube_context: List[Dict] = None,
        sentiment_context: Dict = None
    ) -> str:
        """Build context-aware prompt for standard analysis"""
        prompt_parts = [
            f"Question: {question}",
            "\nAnalyze using the provided context below:",
            "",
        ]
        
        if context_chunks:
            prompt_parts.append("## Document Context:")
            for chunk in context_chunks:
                prompt_parts.append(f"- {chunk.get('filename', 'Unknown source')}: {chunk.get('text', '')[:500]}...")
            prompt_parts.append("")
            
        if news_context:
            prompt_parts.append("## Recent News Context:")
            for news in news_context:
                prompt_parts.append(f"- {news.get('title', 'News')}: {news.get('text', '')[:300]}...")
            prompt_parts.append("")
            
        if youtube_context:
            prompt_parts.append("## YouTube Context:")
            for video in youtube_context:
                prompt_parts.append(f"- {video.get('title', 'Video')}: {video.get('description', '')[:200]}...")
            prompt_parts.append("")
            
        if sentiment_context:
            prompt_parts.append("## Public Sentiment Context:")
            prompt_parts.append(str(sentiment_context.get('sentiment_summary', 'No summary available')))
            
        return "\n".join(prompt_parts)

    def _create_decision_report_prompt(
        self,
        question: str,
        context_chunks: List[Dict] = None,
        news_context: List[Dict] = None,
        sentiment_context: Dict = None,
        youtube_context: List[Dict] = None
    ) -> str:
        """Build prompt specifically for structured decision report"""
        prompt = self.create_prompt(question, context_chunks, news_context, youtube_context, sentiment_context)
        prompt += "\n\nBased on this context, generate a complete structured decision report in the specified JSON format."
        return prompt

# Initialize service instance
llm_service = LLMService(api_key=settings.GROQ_API_KEY)
