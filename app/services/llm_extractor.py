import json
import logging
from tenacity import retry, wait_exponential, stop_after_attempt

from app.schemas.models import Resume
from app.extractors.document_reader import extract_resume_text
from app.core.llm_client import client, MODEL

logger = logging.getLogger(__name__)

# Add Auto-Retry (Tries 3 times, waits exponentially between failures)
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
async def extract_structured_resume(file_path: str) -> Resume:
    """Extracts text from a file and returns a validated Pydantic Resume object."""
    
    logger.info(f"Reading document: {file_path}")
    raw_resume_content = extract_resume_text(file_path)

    schema = Resume.model_json_schema()
    
    sys_message = {
        "role": "system",
        "content": f"Give me the output in strictly based json output schema: {json.dumps(schema)}"
    }
    user_message = {
        "role": "user",
        "content": f"This is a candidate's resume. Please extract the personal and professional information.\n\nResume Content:\n{raw_resume_content}"
    }

    # LLM calling for extraction in structured o/p
    logger.info("Sending prompt to Groq API...")
    response = await client.chat.completions.create(
        model=MODEL, 
        messages=[sys_message, user_message], 
        response_format={"type": "json_object"}
    )
    
    # Track Tokens & Costs!
    usage = response.usage
    logger.info(f"API Success! Tokens Used - Prompt: {usage.prompt_tokens} | Completion: {usage.completion_tokens}")

    answer_string = response.choices[0].message.content
    
    # The Safety Net: Validate the raw JSON string back into a Python Object
    logger.info("Validating JSON output against Pydantic Schema...")
    validated_resume = Resume.model_validate_json(answer_string)
    
    return validated_resume