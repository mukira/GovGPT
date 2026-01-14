"""
Query Classification Utility
Determines if a user query needs a decision report or exploratory response
"""

def classify_query(message: str) -> str:
    """
    Classify user query as 'decision' or 'exploratory'
    
    Decision queries typically:
    - Ask "should we...?"
    - Request recommendations
    - Ask about policy choices
    - Require approval/rejection decisions
    
    Exploratory queries typically:
    - Ask "what is...?"
    - Request explanations
    - Ask for historical context
    - Seek general information
    
    Args:
        message: User's question
        
    Returns:
        'decision' or 'exploratory'
    """
    lower_msg = message.lower().strip()
    
    # Strong decision indicators (high confidence)
    strong_decision_keywords = [
        'should we', 'should i', 'should kenya', 'should the',
        'recommend', 'approval', 'approve', 'decide',
        'allocate', 'reallocate', 'fund', 'defund',
        'implement', 'adopt', 'reject', 'accept',
        'expand', 'reduce', 'increase', 'decrease',
        'prioritize', 'choose between', 'select',
        'go ahead', 'proceed with', 'move forward'
    ]
    
    # Moderate decision indicators
    moderate_decision_keywords = [
        'policy', 'budget', 'funding', 'investment',
        'program', 'initiative', 'project',
        'benefits', 'costs', 'trade-offs', 'tradeoffs',
        'impact', 'consequences', 'effects',
        'options', 'alternatives', 'choices'
    ]
    
    # Exploratory indicators (override decision classification)
    exploratory_keywords = [
        'what is', 'what are', 'who is', 'who are',
        'when did', 'when was', 'where is', 'where are',
        'how does', 'how do', 'how did',
        'explain', 'describe', 'define', 'tell me about',
        'history of', 'background on', 'overview of',
        'summarize', 'summary of', 'list', 'show me'
    ]
    
    # Check for strong exploratory indicators first
    if any(keyword in lower_msg for keyword in exploratory_keywords):
        # Exception: "what should" or "how should" are still decision queries
        if 'should' in lower_msg:
            return 'decision'
        return 'exploratory'
    
    # Check for strong decision indicators
    if any(keyword in lower_msg for keyword in strong_decision_keywords):
        return 'decision'
    
    # Check for moderate decision indicators + question structure
    if any(keyword in lower_msg for keyword in moderate_decision_keywords):
        # If it ends with a question mark and contains decision context
        if '?' in lower_msg:
            return 'decision'
    
    # Default to exploratory for general questions
    return 'exploratory'


def get_query_confidence(message: str) -> dict:
    """
    Get classification with confidence score
    
    Returns:
        {
            'type': 'decision' or 'exploratory',
            'confidence': float (0.0 to 1.0),
            'reasoning': str
        }
    """
    classification = classify_query(message)
    lower_msg = message.lower().strip()
    
    # Calculate confidence based on keyword matches
    strong_keywords = ['should', 'approve', 'recommend', 'decide']
    moderate_keywords = ['policy', 'budget', 'impact', 'options']
    exploratory_keywords = ['what is', 'explain', 'history']
    
    strong_matches = sum(1 for kw in strong_keywords if kw in lower_msg)
    moderate_matches = sum(1 for kw in moderate_keywords if kw in lower_msg)
    exploratory_matches = sum(1 for kw in exploratory_keywords if kw in lower_msg)
    
    if classification == 'decision':
        if strong_matches >= 2:
            confidence = 0.95
            reasoning = f"Strong decision language detected: {strong_matches} indicators"
        elif strong_matches >= 1:
            confidence = 0.85
            reasoning = "Clear decision keyword present"
        elif moderate_matches >= 2:
            confidence = 0.70
            reasoning = "Multiple policy/decision context keywords"
        else:
            confidence = 0.60
            reasoning = "Policy context suggests decision query"
    else:  # exploratory
        if exploratory_matches >= 1:
            confidence = 0.90
            reasoning = "Clear exploratory language"
        else:
            confidence = 0.70
            reasoning = "No strong decision indicators"
    
    return {
        'type': classification,
        'confidence': confidence,
        'reasoning': reasoning
    }
