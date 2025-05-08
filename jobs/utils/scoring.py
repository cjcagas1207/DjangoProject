from rapidfuzz import fuzz

# Define weights
weights = {
    "qualifications": 0.40,
    "skills": 0.30,
    "experience": 0.20,
    "traits": 0.10
}

# Threshold for passing
THRESHOLD_SCORE = 70.0

# Sample data
job_description = {
    "qualifications": "Master's degree in Computer Science, 2 years of teaching experience",
    "skills": "Subject-matter expertise, instructional skills, research",
    "experience": "Develop curriculum, supervise research, conduct assessments",
    "traits": "Strong communication, leadership, lifelong learning"
}

applicant_resume = {
    "qualifications": "Master's degree in Information Technology, 3 years of teaching",
    "skills": "Subject-matter expertise, basic research",
    "experience": "Develop curriculum, supervise projects",
    "traits": "Strong communication, teamwork, adaptability"
}

# Scoring function
def compute_fuzzy_score(job_text, applicant_text):
    return fuzz.token_sort_ratio(job_text, applicant_text)

# Apply scoring
def compute_total_score(job, resume):
    scores = {}
    total_score = 0.0

    for key in weights:
        score = compute_fuzzy_score(job[key], resume[key])
        weighted_score = score * weights[key]
        scores[key] = {
            "raw_score": score,
            "weighted_score": weighted_score
        }
        total_score += weighted_score

    return scores, round(total_score, 2)

# Evaluation
scores, total = compute_total_score(job_description, applicant_resume)
result = "Pass" if total >= THRESHOLD_SCORE else "Fail"

# Display results
print("\n=== Scoring Results ===")
for k, v in scores.items():
    print(f"{k.title()}: Raw Score = {v['raw_score']}%, Weighted = {v['weighted_score']:.2f}")

print(f"Total Score: {total}%")
print(f"Result: {result}")
