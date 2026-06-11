# Job Search Dashboard

A local web app that aggregates internship/co-op, new grad, undergrad research,
and startup postings, then ranks them based on your preferences and resume.

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Configure ranking

1. Edit `config/preferences.yaml` to set role keywords, location preferences,
   preferred companies, excluded companies, sponsorship needs, and acceptable
   degree levels.
2. Paste a plain-text version of your resume into `config/resume.txt`. Words
   from your resume that match a job's title/category give it a ranking boost.

## Run

```bash
./venv/bin/python app.py
```

Then open http://127.0.0.1:5050

Note: by default the app only shows jobs posted within the last 7 days. You
can change this by adding the `max_age_days` query parameter to the URL. For
example, `?max_age_days=14` shows jobs from the last 14 days. Setting
`max_age_days=0` will show no jobs by age, and negative values are ignored.

## Data sources

- **Internship/Co-op** and **New Grad**: pulled live from the community-maintained
  SimplifyJobs / vanshb03 GitHub repos (cached for 6 hours, click "Refresh
  listings" to force an update).
- **Undergrad Research** and **Startup**: add manually via "+ Add research /
  startup posting" — these are stored in `manual_jobs.json`.

## How ranking works

Each job gets an "ease of getting in" score from `scoring.py` based on:
- Skill keyword matches (FPGA, Verilog, PyTorch, LiDAR, embedded,
  cybersecurity, etc. — tuned to your background)
- Security clearance mentions (big bonus — you hold an active Secret
  clearance, which most applicants don't)
- Degree requirement fit (penalty if a job demands a degree level you
  don't have yet)
- Competitive company penalty (FAANG/quant-style companies score lower
  since they're harder to land)
- Resume keyword overlap with the job title/category
- Recency decay (older postings score slightly lower)

**Location is intentionally not used in scoring at all.**

Hover over a job's score to see the breakdown. Adjust weights in
`config/preferences.yaml` and refresh the page — no restart needed.
