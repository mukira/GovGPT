"""
Chat API Endpoints
Handles conversational Q&A and decision report generation
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import json

from app.services.chat_service import chat_service


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat"""
    message: str = Field(..., description="User's question or message")
    include_news: bool = Field(True, description="Include news context")
    include_sentiment: bool = Field(True, description="Include sentiment context")


class ChatResponse(BaseModel):
    """Response model for chat"""
    answer: str
    citations: List[Dict]
    context_used: Dict


class ReportRequest(BaseModel):
    """Request model for decision report generation"""
    question: str = Field(..., description="Policy question or decision to analyze")
    include_news: bool = Field(True, description="Include news context in analysis")
    include_sentiment: bool = Field(True, description="Include public sentiment in analysis")


class DecisionReport(BaseModel):
    """Response model for decision report"""
    decision_required: str
    timeline: str
    accountable: str
    executive_summary: Dict[str, Any]
    options: List[Dict[str, Any]]
    recommended_option: str
    recommendation_rationale: str
    impact_breakdown: Dict[str, Any]
    risks_mitigations: List[Dict[str, Any]]
    data_sources: List[str]
    assumptions: List[str]
    limitations: str
    next_steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("/message", response_model=ChatResponse)
async def send_message(msg: ChatRequest):
    """
    Send a message and get a complete response
    
    Request body:
    - message: User's question
    - include_news: Include news context (default: true)
    - include_sentiment: Include sentiment context (default: true)
    """
    try:
        response = chat_service.process_message(
            message=msg.message,
            include_news=msg.include_news,
            include_sentiment=msg.include_sentiment
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_message(msg: ChatRequest):
    """
    Stream chat response in real-time (SSE)
    
    Events:
    - context: Context gathering complete
    - content: Response chunk
    - citations: Sources at the end
    """
    def generate():
        try:
            for chunk in chat_service.stream_message(
                message=msg.message,
                include_news=msg.include_news,
                include_sentiment=msg.include_sentiment
            ):
                # Format as Server-Sent Event
                data = json.dumps(chunk)
                yield f"data: {data}\n\n"
        except Exception as e:
            error_data = json.dumps({'type': 'error', 'data': str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def chat_health():
    """Check if chat services are initialized"""
    from app.services.vector_service import vector_service
    from app.services.llm_service import llm_service
    
    return {
        "vector_db": "initialized" if vector_service.client else "not_initialized",
        "llm": "initialized" if chat_service else "pending",
        "status": "operational"
    }


@router.post("/generate-report")
async def generate_decision_report(request: ReportRequest):
    """
    Generate structured decision report for government decision-makers
    
    **Returns a comprehensive report with:**
    - Executive summary with recommendation
    - 2-4 options comparison
    - Impact breakdown (economic, social, regional, population)
    - Risk assessment with mitigations
    - Next steps with timelines
    - Data sources and assumptions
    
    **Example:**
    ```json
    {
        "question": "Should we reallocate 10% of education budget to rural schools?"
    }
    ```
    """
    try:
        report = chat_service.generate_decision_report(
            question=request.question,
            include_news=request.include_news,
            include_sentiment=request.include_sentiment
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
