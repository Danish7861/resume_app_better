import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import re
from collections import Counter
import streamlit as st
import json

# Load environment variables
load_dotenv()

# Get API key from .env
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def fix_cv(cv_text, jd_text):
    prompt = f"""
    You are a CV optimization expert.
    Candidate CV:
    {cv_text}

    Job Description:
    {jd_text}

    Rewrite the CV to better match the job description while keeping honesty.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def ats_score_check(cv_text, jd_text):
    prompt = f"""
            You are an ATS (Applicant Tracking System) and CV optimization expert. 
            Your task is to evaluate how well the candidate's CV matches the Job Description (JD) 
            and then provide a clear ATS-style report.

            Candidate CV:
            {cv_text}

            Job Description:
            {jd_text}

            Your output must include:
            1. **ATS Score (0–100%)** – based on keyword match, relevance, and context.
            2. **Matched Keywords** – list keywords/phrases from JD found in the CV.
            3. **Missing Keywords** – list important JD terms missing in the CV.
            """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    ats_report = response.choices[0].message.content.strip()
    return ats_report

    

def ats_score_check_optimized(fixed_cv, jd_text):
    prompt = f"""
    You are an ATS (Applicant Tracking System). 
    Evaluate how well the candidate's CV matches the Job Description.
    
    Candidate CV:
    {fixed_cv}

    Job Description:
    {jd_text}

    Return ONLY a ATS NUMBER with this structure:
    {{
        "ats_score": <number between 0 and 100>
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # keep deterministic
    )

    # Extract text and parse with Pydantic
    result = response.choices[0].message.content.strip()
    # Parse JSON
    parsed = json.loads(result)
    ats_score = float(parsed["ats_score"])
    #ats_result = ATSScore.model_validate_json(result)

    return ats_score

