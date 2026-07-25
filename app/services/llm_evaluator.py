import json
import logging
from tenacity import retry, wait_exponential, stop_after_attempt

from app.schemas.models import Resume, MatchResult
from app.core.llm_client import client, MODEL

logger = logging.getLogger(__name__)


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
async def evaluate_resume_jd(resume: Resume, job_description: str) -> MatchResult:
    """Compares a candidate's structured Resume against a Job Description 
    and returns a validated MatchResult object.
    """
    logger.info(f"Starting candidate evaluation for: {resume.name}")
    
    schema = MatchResult.model_json_schema()
    
    system_message = {
        "role": "system",
        "content": (
            "You are an expert technical HR recruiter. Strictly evaluate the candidate's "
            "structured resume data against the provided Job Description. "
            f"You MUST output JSON matching this schema: {json.dumps(schema)}"
        )
    }
    
    user_message = {
        "role": "user",
        "content": (
            f"Candidate Resume Data:\n{resume.model_dump_json()}\n\n"
            f"Job Description:\n{job_description}"
        )
    }
    
    logger.info("Sending evaluation prompt to Groq API...")
    response = await client.chat.completions.create(
        model=MODEL, 
        messages=[system_message, user_message],
        response_format={"type": "json_object"}
    )

    # Track usage
    usage = response.usage
    logger.info(f"Evaluation Complete! Tokens - Prompt: {usage.prompt_tokens} | Completion: {usage.completion_tokens}")

    answer_string = response.choices[0].message.content
    
    logger.info("Validating evaluation output against MatchResult schema...")
    validated_match = MatchResult.model_validate_json(answer_string)
    
    return validated_match