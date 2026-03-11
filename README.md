# Resume Parsing and Job Matching System

A rule-based system that parses resumes (PDF) and matches them against job descriptions. **No LLMs or AI APIs used.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API Framework | FastAPI |
| PDF Parsing | pdfplumber |
| Text Extraction | Regex (re) |
| UI | Jinja2 + HTML/CSS/JS |

---

## Project Structure

```
resume-matcher/
├── main.py                  # FastAPI app and all API routes
├── requirements.txt         # Python dependencies
├── parsers/
│   ├── resume_parser.py     # PDF parsing — name, skills, experience, salary
│   └── jd_parser.py        # JD parsing — skills, experience, salary, summary
├── matcher/
│   └── matcher.py          # Skill analysis and score calculation
├── utils/
│   └── skills_dict.py      # Master skills dictionary (100+ skills)
├── templates/
│   └── index.html          # Web UI
└── uploads/                # Temp folder for uploaded files (auto-created)
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/AkhilBejjanki/resume-matcher.git
cd resume-matcher
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
python main.py
```

### 5. Open in browser

```
http://localhost:8000
```

---

## How to Use

1. Upload your **resume as a PDF**
2. Paste one or more **job descriptions** (add as many as you want)
3. Click **Match Resume**
4. View results — candidate summary, skill analysis per job, matching score
5. Download the **output JSON** from the results section

---

## API Endpoints

All endpoints are available via Swagger UI at `http://localhost:8000/docs`

### `POST /api/match` — Main endpoint
Upload resume + JDs, returns full matching output.

**Form data:**
- `resume` — PDF file
- `jds` — JSON string:
```json
[
  { "id": "JD001", "role": "Backend Developer", "text": "full jd text..." }
]
```

### `POST /api/parse-resume`
Parse resume PDF only. Returns name, skills, experience, salary.

### `POST /api/parse-jd`
Parse a single JD text. Returns skills, experience, salary, summary.

---

## Output JSON Format

```json
{
  "name": "John Doe",
  "salary": null,
  "yearOfExperience": 1.0,
  "resumeSkills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
  "matchingJobs": [
    {
      "jobId": "JD001",
      "role": "Backend Developer",
      "aboutRole": "Responsible for backend development using Python...",
      "skillsAnalysis": [
        { "skill": "Python", "presentInResume": true },
        { "skill": "Kubernetes", "presentInResume": false }
      ],
      "matchingScore": 66.67
    }
  ]
}
```

---

## How It Works (No LLMs)

| Task | Approach |
|---|---|
| PDF text extraction | `pdfplumber` reads raw text from PDF |
| Name extraction | Regex — scans top lines for capitalized 2–4 word patterns |
| Skills extraction | Word-boundary regex matched against a 100+ skills dictionary |
| Salary extraction | Regex patterns for USD ranges, LPA, INR formats |
| Experience extraction | Regex for explicit mentions, degree+years patterns, fresher detection |
| Required vs Optional split | Section header detection (Required / Desired / Good to have) |
| Matching score | `(matched JD skills / total JD skills) × 100` |


