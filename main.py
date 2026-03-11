import os
import json
import uuid
import shutil

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from parsers.resume_parser import parse_resume
from matcher.matcher import match_resume_to_jobs

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI(
    title="Resume Matcher API",
    description="Rule-based Resume Parsing and Job Matching System (No LLMs)",
    version="1.0.0",
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────────
# UI ROUTE
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ─────────────────────────────────────────────
# API: PARSE RESUME ONLY
# ─────────────────────────────────────────────

@app.post("/api/parse-resume")
async def api_parse_resume(resume: UploadFile = File(...)):
    """
    Upload a resume PDF and get parsed structured data.
    Returns: name, salary, yearOfExperience, resumeSkills
    """
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded file temporarily
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{resume.filename}")
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    try:
        parsed = parse_resume(temp_path)
        # Remove internal raw text from response
        parsed.pop("_rawText", None)
        return JSONResponse(content=parsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    finally:
        os.remove(temp_path)


# ─────────────────────────────────────────────
# API: MATCH RESUME TO JDs
# ─────────────────────────────────────────────

@app.post("/api/match")
async def api_match(
    resume: UploadFile = File(...),
    jds: str = Form(...),
):
    """
    Upload a resume PDF + JSON list of JDs, get full matching output.

    jds format (send as form field):
    [
        { "id": "JD001", "role": "Backend Developer", "text": "...full JD text..." },
        { "id": "JD002", "role": "Full Stack Engineer", "text": "..." }
    ]
    """
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Parse JDs JSON
    try:
        jd_list = json.loads(jds)
        if not isinstance(jd_list, list) or len(jd_list) == 0:
            raise ValueError("jds must be a non-empty list.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JDs format. Expected JSON array.")

    # Save resume temporarily
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{resume.filename}")
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    try:
        resume_data = parse_resume(temp_path)
        result = match_resume_to_jobs(resume_data, jd_list)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")
    finally:
        os.remove(temp_path)


# ─────────────────────────────────────────────
# API: PARSE JD ONLY
# ─────────────────────────────────────────────

@app.post("/api/parse-jd")
async def api_parse_jd(
    jd_id: str = Form(default="JD001"),
    role: str = Form(...),
    jd_text: str = Form(...),
):
    """
    Parse a single JD text and return structured data.
    """
    from parsers.jd_parser import parse_jd
    try:
        parsed = parse_jd(jd_id=jd_id, role=role, jd_text=jd_text)
        parsed.pop("_rawText", None)
        return JSONResponse(content=parsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
