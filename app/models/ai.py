from pydantic import BaseModel, Field


class AiAdvisorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AiAdvisorContextUsed(BaseModel):
    dashboard: bool
    alerts: bool
    recommendations: bool
    report: bool


class AiAdvisorResponse(BaseModel):
    answer: str
    model: str
    context_used: AiAdvisorContextUsed
