from pydantic import BaseModel


class GenerateRequest(BaseModel):
    job_application_id: str
    user_id: str
    job_description: str = ""


class GenerateResponse(BaseModel):
    id: str
    title: str
    type: str
    content_text: str
    pdf_path: str = ""
