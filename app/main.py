import os
import tempfile
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.services.llm_extractor import extract_structured_resume
from app.services.llm_evaluator import evaluate_resume_jd

# Setup Global Logging (Runs once when server starts)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Parsing API", version="1.0")
logger.info("Initializing AI Resume Parsing API Server...")

# DRY Helper Function to handle file uploads cleanly
async def save_temp_file(file: UploadFile) -> str:
    """Validates and saves an uploaded file temporarily to disk."""
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed.")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file.write(await file.read())
        return temp_file.name

# Extraction Endpoint
@app.post("/extract")
async def extract_resume(file: UploadFile = File(...)):
    """Upload a PDF/Word resume and get back structured JSON extracted data."""
    temp_path = await save_temp_file(file)
    
    try:
        logger.info(f"Received request to extract resume: {file.filename}")
        # Using 'await' because our service is asynchronous
        resume_data = await extract_structured_resume(temp_path)
        return {"status": "success", "data": resume_data}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_path) # Clean up temp file safely


# Evaluation Endpoint
@app.post("/evaluate")
async def evaluate_candidate(
    file: UploadFile = File(...), 
    job_description: str = Form(...)
):
    """Upload a resume file AND a job description to get a match score and evaluation."""
    temp_path = await save_temp_file(file)

    try:
        logger.info(f"Received request to evaluate candidate against JD for file: {file.filename}")
        
        # Step 1: Asynchronously extract structured resume data
        resume_data = await extract_structured_resume(temp_path)
        
        # Step 2: Asynchronously evaluate resume against the job description
        evaluation_result = await evaluate_resume_jd(resume_data, job_description)
        
        return {"status": "success", "data": evaluation_result}
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_path)