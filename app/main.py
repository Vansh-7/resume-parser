import os
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.services.llm_extractor import extract_structured_resume
from app.services.llm_evaluator import evaluate_resume_jd

# --- SET UP GLOBAL LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
# ----------------------------------

app = FastAPI(title = "AI Resume Parsing API")
logger.info("Starting up FastAPI Server...")

# --- HELPER FUNCTION ---
async def save_temp_file(file: UploadFile) -> str:
    """Saves an UploadFile to disk and returns the file path."""
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed.")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file.write(await file.read())
        return temp_file.name

# --- CLEAN ENDPOINTS ---
@app.post("/extract")
async def extract_resume(file: UploadFile = File(...)):
    temp_path = await save_temp_file(file) # Just one line now!
    try:
        resume_data = await extract_structured_resume(temp_path)
        return {"status": "success", "data": resume_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_path)

@app.post("/evaluate")
async def evaluate_candidate(file: UploadFile = File(...), job_description: str = Form(...)):
    temp_path = await save_temp_file(file) # Reusing the helper function!
    try:
        resume_data = await extract_structured_resume(temp_path)
        evaluation_result = await evaluate_resume_jd(resume_data, job_description)
        return {"status": "success", "data": evaluation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_path)