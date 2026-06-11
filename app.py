import json
import os
import time
import uuid
from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request, url_for

import data_sources
import scoring
import skills_profile

app = Flask(__name__)

MANUAL_JOBS_PATH = os.path.join(os.path.dirname(__file__), "manual_jobs.json")


def load_manual_jobs():
    if not os.path.exists(MANUAL_JOBS_PATH):
        return []
    with open(MANUAL_JOBS_PATH) as f:
        return json.load(f)


def save_manual_jobs(jobs):
    with open(MANUAL_JOBS_PATH, "w") as f:
        json.dump(jobs, f, indent=2)


@app.route("/")
def index():
    listing_type = request.args.get("type", "all")
    fit_tier = request.args.get("fit", "all")
    query = request.args.get("q", "").strip().lower()
    show_inactive = request.args.get("show_inactive") == "1"
    # New: allow filtering by age in days; default to 7 days
    try:
        max_age_days = int(request.args.get("max_age_days", "7"))
        if max_age_days < 0:
            max_age_days = None
    except Exception:
        max_age_days = 7

    jobs = data_sources.fetch_all_listings()
    jobs += load_manual_jobs()

    prefs = scoring.load_preferences()
    resume_keywords = scoring.load_resume_keywords()
    ranked = scoring.rank_jobs(jobs, prefs, resume_keywords)

    if not show_inactive:
        ranked = [j for j in ranked if j.get("active", True)]

    if listing_type != "all":
        ranked = [j for j in ranked if j.get("listing_type") == listing_type]

    if fit_tier != "all":
        ranked = [j for j in ranked if j.get("fit_tier") == fit_tier]

    if query:
        ranked = [
            j for j in ranked
            if query in j.get("title", "").lower()
            or query in j.get("company", "").lower()
            or query in j.get("category", "").lower()
            or query in " ".join(j.get("locations", [])).lower()
        ]

    # Filter to jobs posted within `max_age_days` if available. We expect
    # `date_posted` to be normalized to epoch seconds (float) by
    # `data_sources._normalize`. If the field is missing, keep the job.
    if max_age_days is not None:
        cutoff = time.time() - (max_age_days * 24 * 60 * 60)
        def is_within_one_week(job):
            dp = job.get("date_posted")
            if dp is None:
                return False
            try:
                return float(dp) >= cutoff
            except Exception:
                return False

        ranked = [j for j in ranked if is_within_one_week(j)]

    cache_status = data_sources.cache_status()

    return render_template(
        "index.html",
        jobs=ranked[:300],
        total=len(ranked),
        listing_type=listing_type,
        fit_tier=fit_tier,
        query=request.args.get("q", ""),
        show_inactive=show_inactive,
        cache_status=cache_status,
        now=time.time(),
    )


@app.route("/skills")
def skills():
    return render_template(
        "skills.html",
        skills=skills_profile.get_skills(),
        level_labels=skills_profile.LEVEL_LABELS,
    )


@app.route("/refresh", methods=["POST"])
def refresh():
    data_sources.fetch_all_listings(force_refresh=True)
    params = {k: v for k, v in request.args.items() if not str(k).startswith("_")}
    qs = ("?" + urlencode(params)) if params else ""
    return redirect(url_for("index") + qs)


@app.route("/add", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        jobs = load_manual_jobs()
        jobs.append({
            "id": str(uuid.uuid4()),
            "title": request.form.get("title", "").strip(),
            "company": request.form.get("company", "").strip(),
            "category": request.form.get("category", "").strip(),
            "locations": [
                loc.strip() for loc in request.form.get("locations", "").split(",") if loc.strip()
            ],
            "url": request.form.get("url", "").strip(),
            "company_url": "",
            "active": True,
            "terms": [],
            "date_posted": time.time(),
            "date_updated": time.time(),
            "sponsorship": "",
            "degrees": [],
            "listing_type": request.form.get("listing_type", "research"),
            "source": "manual",
        })
    save_manual_jobs(jobs)
    params = {k: v for k, v in request.args.items() if not str(k).startswith("_")}
    qs = ("?" + urlencode(params)) if params else ""
    return redirect(url_for("index") + qs)

    return render_template("add_job.html")


@app.route("/remove/<job_id>", methods=["POST"])
def remove_job(job_id):
    jobs = load_manual_jobs()
    jobs = [j for j in jobs if j["id"] != job_id]
    save_manual_jobs(jobs)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
