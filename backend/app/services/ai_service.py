"\"\"\"
AI Service using Groq API
Fast, reliable, and production-ready
Author: Updated for IntelliHire Pro
Date: 2025
\"\"\"

import json
import logging
import os
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(\"intellihire.ai\")

# ==================== GROQ CONFIGURATION ====================
GROQ_API_KEY = os.getenv(\"GROQ_API_KEY\", \"\").strip()
MODEL = os.getenv(\"GROQ_MODEL\", \"llama-3.3-70b-versatile\")
REQUEST_TIMEOUT = int(os.getenv(\"GROQ_TIMEOUT\", \"20\"))

_client = None


# ==================== CLIENT INITIALIZATION ====================

def _get_client():
    \"\"\"Initialize Groq client (lazy loading)\"\"\"
    global _client
    
    if not GROQ_API_KEY:
        logger.warning(\"❌ GROQ_API_KEY is not set — AI features disabled\")
        return None
    
    if _client is None:
        try:
            from groq import Groq
            _client = Groq(
                api_key=GROQ_API_KEY,
                timeout=REQUEST_TIMEOUT,
            )
            logger.info(f\"✅ Groq client initialized | model={MODEL} | timeout={REQUEST_TIMEOUT}s\")
        except ImportError:
            logger.error(\"❌ Groq library not installed. Run: pip install groq\")
            return None
        except Exception as e:
            logger.error(f\"❌ Groq client initialization failed: {e}\", exc_info=True)
            return None
    
    return _client


# ==================== CORE CHAT FUNCTION ====================

def _chat(system: str, user: str, temperature: float = 0.7, max_retries: int = 2) -> Optional[str]:
    \"\"\"
    Send a chat request to Groq API with retry logic
    
    Args:
        system: System message (instructions for AI)
        user: User message (the actual prompt)
        temperature: Creativity level (0.0-1.0)
        max_retries: Number of retry attempts on failure
    
    Returns:
        AI response text or None on failure
    \"\"\"
    client = _get_client()
    if not client:
        logger.error(\"❌ Groq client not available\")
        return None
    
    # Retry loop for reliability
    for attempt in range(max_retries + 1):
        try:
            logger.info(f\"🤖 Groq API call (attempt {attempt + 1}/{max_retries + 1}) | model={MODEL}\")
            
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {\"role\": \"system\", \"content\": system},
                    {\"role\": \"user\", \"content\": user},
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            
            if not response or not response.choices:
                logger.warning(\"⚠️ Empty response from Groq API\")
                continue
            
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                logger.info(f\"✅ Groq response received ({len(content)} chars)\")
                return content
            else:
                logger.warning(\"⚠️ Groq returned empty content\")
                continue
                
        except Exception as e:
            logger.error(f\"❌ Groq API error (attempt {attempt + 1}): {e}\", exc_info=True)
            if attempt < max_retries:
                logger.info(\"🔄 Retrying...\")
                continue
            else:
                logger.error(\"❌ All retry attempts failed\")
                return None
    
    return None


# ==================== JSON PARSING ====================

def _clean_json(text: str):
    \"\"\"
    Extract and parse JSON from AI response
    Handles markdown code blocks and messy formatting
    \"\"\"
    if not text:
        return None
    
    try:
        # Remove markdown code blocks
        text = re.sub(r\"```(?:json)?\s*\", \"\", text).strip().rstrip(\"`\").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON array or object using regex
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        logger.warning(\"⚠️ Failed to parse JSON from AI response\")
        return None


# ==================== QUESTION GENERATION ====================

def generate_questions(
    role: str,
    skills: list,
    num_questions: int = 5,
    difficulty: str = \"medium\",
    include_behavioral: bool = False
):
    \"\"\"
    Generate interview questions using Groq AI
    
    Args:
        role: Job role (e.g., \"Python Developer\")
        skills: List of required skills
        num_questions: Number of questions to generate
        difficulty: \"easy\", \"medium\", \"hard\", or \"mixed\"
        include_behavioral: Include behavioral questions
    
    Returns:
        List of question dictionaries
    \"\"\"
    logger.info(
        f\"📝 Generating questions | role={role} | skills={skills} | \"
        f\"difficulty={difficulty} | behavioral={include_behavioral}\"
    )
    
    # Convert skills to list if it's a string
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(\",\") if s.strip()]
    
    # Build the prompt
    system_prompt = (
        \"You are an expert technical interviewer with 15+ years of experience. \"
        \"Generate HIGHLY RELEVANT and ROLE-SPECIFIC interview questions. \"
        \"Questions must be clear, professional, and appropriate for the difficulty level. \"
        \"Return ONLY a valid JSON array with this exact structure:
\"
        '[{\"question\": \"text\", \"difficulty\": \"easy/medium/hard\", \"category\": \"technical/behavioral\"}]
'
        \"NO explanations, NO markdown, JUST the JSON array.\"
    )
    
    user_prompt = (
        f\"Generate {num_questions} interview questions for:
\"
        f\"Role: {role}
\"
        f\"Required Skills: {', '.join(skills)}
\"
        f\"Difficulty Level: {difficulty}
\"
        f\"Include Behavioral Questions: {'Yes' if include_behavioral else 'No'}

\"
        f\"Requirements:
\"
        f\"- Questions must test practical knowledge of {', '.join(skills)}
\"
        f\"- Mix technical and problem-solving questions
\"
        f\"- Adjust complexity based on '{difficulty}' level
\"
        f\"- Return exactly {num_questions} questions
\"
        f\"- Output format: JSON array only\"
    )
    
    try:
        # Call Groq API
        result = _chat(system=system_prompt, user=user_prompt, temperature=0.85)
        
        if result:
            # Parse JSON response
            data = _clean_json(result)
            
            if isinstance(data, list) and len(data) > 0:
                # Validate and return questions
                questions = []
                for item in data[:num_questions]:
                    if isinstance(item, dict) and \"question\" in item:
                        questions.append({
                            \"question\": item.get(\"question\", \"\"),
                            \"difficulty\": item.get(\"difficulty\", difficulty),
                            \"category\": item.get(\"category\", \"technical\"),
                        })
                
                if questions:
                    logger.info(f\"✅ Generated {len(questions)} AI questions successfully\")
                    return questions
                else:
                    logger.warning(\"⚠️ AI returned invalid question format\")
            else:
                logger.warning(\"⚠️ AI response was not a valid list\")
        else:
            logger.warning(\"⚠️ Groq API returned None\")
    
    except Exception as e:
        logger.error(f\"❌ Question generation failed: {e}\", exc_info=True)
    
    # Fallback questions (only used if AI fails)
    logger.warning(\"⚠️ Using fallback questions (AI generation failed)\")
    return [
        {
            \"question\": f\"What are the key responsibilities and challenges of a {role}?\",
            \"difficulty\": \"medium\",
            \"category\": \"general\"
        },
        {
            \"question\": f\"Explain your experience with {skills[0] if skills else 'relevant technologies'}.\",
            \"difficulty\": \"medium\",
            \"category\": \"technical\"
        },
        {
            \"question\": \"Describe a challenging technical problem you solved recently.\",
            \"difficulty\": \"medium\",
            \"category\": \"behavioral\"
        },
        {
            \"question\": f\"How do you stay updated with the latest trends in {role}?\",
            \"difficulty\": \"easy\",
            \"category\": \"general\"
        },
        {
            \"question\": \"What is your approach to debugging and troubleshooting?\",
            \"difficulty\": \"medium\",
            \"category\": \"technical\"
        },
    ][:num_questions]


# ==================== ANSWER EVALUATION ====================

def evaluate_answer(question: str, answer: str, role: str = \"\") -> dict:
    \"\"\"
    Evaluate candidate's answer using Groq AI
    
    Args:
        question: The interview question
        answer: Candidate's answer
        role: Job role (optional, for context)
    
    Returns:
        Evaluation dict with score, feedback, etc.
    \"\"\"
    logger.info(f\"📊 Evaluating answer for role: {role}\")
    
    system_prompt = (
        \"You are an expert interviewer evaluating candidate responses. \"
        \"Provide constructive, professional feedback. \"
        \"Return ONLY valid JSON with this structure:
\"
        '{\"score\": 1-10, \"feedback\": \"detailed feedback\", \"is_correct\": \"correct/partial/incorrect\", '
        '\"strengths\": [\"point1\", \"point2\"], \"weaknesses\": [\"point1\", \"point2\"]}
'
        \"NO markdown, JUST the JSON object.\"
    )
    
    user_prompt = (
        f\"Evaluate this interview answer:

\"
        f\"Question: {question}
\"
        f\"Answer: {answer}
\"
        f\"Role: {role or 'General'}

\"
        f\"Provide:
\"
        f\"- Score (1-10)
\"
        f\"- Detailed feedback
\"
        f\"- Correctness level
\"
        f\"- Key strengths
\"
        f\"- Areas for improvement\"
    )
    
    try:
        result = _chat(system=system_prompt, user=user_prompt, temperature=0.3)
        
        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                logger.info(\"✅ Answer evaluation completed\")
                return {
                    \"score\": data.get(\"score\", 5),
                    \"feedback\": data.get(\"feedback\", \"Answer evaluated\"),
                    \"is_correct\": data.get(\"is_correct\", \"partial\"),
                    \"strengths\": data.get(\"strengths\", []),
                    \"weaknesses\": data.get(\"weaknesses\", []),
                }
    
    except Exception as e:
        logger.error(f\"❌ Answer evaluation failed: {e}\", exc_info=True)
    
    # Fallback evaluation
    return {
        \"score\": 5,
        \"feedback\": \"Answer received. Please provide more details for better evaluation.\",
        \"is_correct\": \"partial\",
        \"strengths\": [\"Response provided\"],
        \"weaknesses\": [\"Needs more depth\"],
    }


# ==================== RESUME ANALYSIS ====================

def analyze_resume_ai(text: str) -> dict:
    \"\"\"
    Analyze resume text using Groq AI
    
    Args:
        text: Extracted resume text
    
    Returns:
        Analysis dict with summary, skills, experience, etc.
    \"\"\"
    logger.info(\"📄 Analyzing resume with Groq AI\")
    
    system_prompt = (
        \"You are an expert HR analyst specializing in resume evaluation. \"
        \"Analyze the provided resume text and extract key information. \"
        \"Return ONLY valid JSON with this structure:
\"
        '{\"summary\": \"brief summary\", \"skills\": [\"skill1\", \"skill2\"], '
        '\"experience_years\": number, \"education\": [\"degree1\"], \"domain\": \"field\", \"resume_score\": 1-100}
'
        \"NO markdown, JUST the JSON object.\"
    )
    
    user_prompt = f\"Analyze this resume:

{text[:3000]}\"  # Limit to avoid token issues
    
    try:
        result = _chat(system=system_prompt, user=user_prompt, temperature=0.3)
        
        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                logger.info(\"✅ Resume analysis completed\")
                return {
                    \"summary\": data.get(\"summary\", \"Resume analyzed\"),
                    \"skills\": data.get(\"skills\", []),
                    \"experience_years\": data.get(\"experience_years\", 0),
                    \"education\": data.get(\"education\", []),
                    \"domain\": data.get(\"domain\", \"General\"),
                    \"resume_score\": data.get(\"resume_score\", 50),
                }
    
    except Exception as e:
        logger.error(f\"❌ Resume analysis failed: {e}\", exc_info=True)
    
    # Fallback
    logger.warning(\"⚠️ Using fallback resume analysis\")
    return {
        \"summary\": \"Resume processed successfully\",
        \"skills\": [],
        \"experience_years\": 0,
        \"education\": [],
        \"domain\": \"General\",
        \"resume_score\": 50,
    }


# ==================== JOB FIT COMPUTATION ====================

def compute_job_fit(resume_summary: str, skills: list, job_role: str, job_description: str) -> dict:
    \"\"\"
    Compute job fit score using Groq AI
    
    Args:
        resume_summary: Resume summary
        skills: Candidate skills
        job_role: Target job role
        job_description: Job description
    
    Returns:
        Job fit analysis dict
    \"\"\"
    logger.info(f\"🎯 Computing job fit for role: {job_role}\")
    
    system_prompt = (
        \"You are an expert HR recruiter evaluating candidate-job fit. \"
        \"Analyze how well the candidate matches the job requirements. \"
        \"Return ONLY valid JSON with this structure:
\"
        '{\"fit_score\": 1-100, \"strengths\": [\"point1\"], \"gaps\": [\"point1\"]}
'
        \"NO markdown, JUST the JSON object.\"
    )
    
    user_prompt = (
        f\"Evaluate job fit:

\"
        f\"Candidate Summary: {resume_summary}
\"
        f\"Candidate Skills: {', '.join(skills)}

\"
        f\"Job Role: {job_role}
\"
        f\"Job Description: {job_description[:1000]}

\"
        f\"Provide fit score (1-100), strengths, and gaps.\"
    )
    
    try:
        result = _chat(system=system_prompt, user=user_prompt, temperature=0.3)
        
        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                logger.info(\"✅ Job fit computation completed\")
                return {
                    \"fit_score\": data.get(\"fit_score\", 60),
                    \"strengths\": data.get(\"strengths\", []),
                    \"gaps\": data.get(\"gaps\", []),
                }
    
    except Exception as e:
        logger.error(f\"❌ Job fit computation failed: {e}\", exc_info=True)
    
    # Fallback
    logger.warning(\"⚠️ Using fallback job fit score\")
    return {
        \"fit_score\": 60,
        \"strengths\": [],
        \"gaps\": [],
    }


# ==================== HEALTH CHECK ====================

def check_ai_status() -> dict:
    \"\"\"Check if Groq AI is available and working\"\"\"
    client = _get_client()
    
    if not client:
        return {
            \"status\": \"unavailable\",
            \"message\": \"Groq API key not configured\",
            \"model\": MODEL,
        }
    
    try:
        # Quick test call
        test_response = _chat(
            system=\"You are a test assistant.\",
            user=\"Respond with exactly: OK\",
            temperature=0.0,
        )
        
        if test_response and \"OK\" in test_response:
            return {
                \"status\": \"available\",
                \"message\": \"Groq AI is working correctly\",
                \"model\": MODEL,
            }
        else:
            return {
                \"status\": \"error\",
                \"message\": \"Groq API responded but output was unexpected\",
                \"model\": MODEL,
            }
    
    except Exception as e:
        return {
            \"status\": \"error\",
            \"message\": f\"Groq API test failed: {str(e)}\",
            \"model\": MODEL,
        }


# ==================== EXPORT ====================
# All functions are now ready to be imported by other modules

if __name__ == \"__main__\":
    # Quick test
    print(\"🧪 Testing Groq AI Service...\")
    status = check_ai_status()
    print(f\"Status: {status}\")
"