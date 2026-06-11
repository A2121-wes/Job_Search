"""A self-assessment of your current skill levels, based on your resume.

This is intentionally honest/calibrated, not flattering. Levels are 1-5:
  1 = Beginner       -- exposed to it, limited hands-on use
  2 = Novice         -- completed a real project/task with it
  3 = Intermediate   -- comfortable, used it across multiple contexts
  4 = Advanced       -- deep, sustained, real-world responsibility
  5 = Expert/Top-tier -- specialist level, could mentor others / publish

Edit this file as your experience grows.
"""

LEVEL_LABELS = {
    1: "Beginner",
    2: "Novice",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert / Top-tier",
}

SKILLS = [
    {
        "name": "C / C++",
        "level": 2,
        "evidence": "Used for model optimization (quantization/pruning) in the FPGA "
                    "research apprenticeship -- real but short-duration, narrow scope.",
        "improve": "Build a non-trivial standalone C++ project (data structures, "
                    "a small systems tool) outside of a guided research context.",
    },
    {
        "name": "Python",
        "level": 2,
        "evidence": "Used for LiDAR/geospatial processing and ML pipelines in research "
                    "roles, but always within existing tooling/frameworks.",
        "improve": "Write and ship a project from scratch (CLI tool, API, data "
                    "pipeline) without a research advisor's existing codebase.",
    },
    {
        "name": "JavaScript",
        "level": 1,
        "evidence": "No dedicated project listed; minimal exposure compared to Swift.",
        "improve": "Pair with a small web project if you want this to count as a skill.",
    },
    {
        "name": "Swift / SwiftUI",
        "level": 3,
        "evidence": "Architected and shipped a complete iOS app with Firebase backend "
                    "for the Congressional App Challenge -- a full project lifecycle.",
        "improve": "Add tests, CI, and a second app to show it wasn't a one-off.",
    },
    {
        "name": "Verilog / FPGA / Vivado",
        "level": 2,
        "evidence": "~3 month research apprenticeship designing CNN accelerators on "
                    "FPGAs -- real hands-on hardware design, but short tenure.",
        "improve": "Extend this with a personal FPGA project (e.g. a small RISC-V "
                    "core or signal processing block) to prove it wasn't a one-time gig.",
    },
    {
        "name": "Machine Learning / PyTorch",
        "level": 2,
        "evidence": "Applied ML for terrain classification (LiDAR) and model "
                    "quantization/pruning (FPGA) -- applied use, not theory-deep.",
        "improve": "Take a rigorous ML course (math-heavy, not just API usage) and "
                    "implement a model from scratch (no high-level libraries).",
    },
    {
        "name": "LiDAR / Geospatial Data",
        "level": 1,
        "evidence": "Current NCALM research role just started (May 2026) -- early days.",
        "improve": "Stay in the role 1-2 years, aim for a poster/paper with the lab.",
    },
    {
        "name": "Networking / RF / Satellite Comms",
        "level": 4,
        "evidence": "2+ years as an Army Reserve Signal Support Specialist: configured "
                    "satellite systems, tactical radios, and network devices in real "
                    "operational environments with 100% readiness requirements.",
        "improve": "This is a genuine strength. Pair it with a civilian "
                    "certification (CCNA, Security+) to translate it for non-DoD employers.",
    },
    {
        "name": "Cybersecurity / Encryption",
        "level": 3,
        "evidence": "Implemented encryption protocols and applied cybersecurity "
                    "principles to protect Army networks -- real operational use.",
        "improve": "CompTIA Security+ or similar would formalize this for civilian roles.",
    },
    {
        "name": "Active Secret Clearance",
        "level": 4,
        "evidence": "Active U.S. government Secret clearance via Army Reserve service "
                    "-- rare among undergrads and a major differentiator for "
                    "defense/aerospace/govt-contractor roles.",
        "improve": "Maintain it (don't let it lapse) -- it's one of your biggest assets.",
    },
    {
        "name": "Leadership / Team Management",
        "level": 4,
        "evidence": "Distinguished Honor Graduate (AIT); curriculum development, team "
                    "management, and mentorship responsibilities in the Army.",
        "improve": "Carry this into civilian/academic settings -- e.g. mentor newer "
                    "students in your research lab, lead a student org project.",
    },
]


def get_skills():
    return SKILLS
