from rapidfuzz import fuzz

# Define weights based on thesis
weights = {
    "qualifications": 0.40,
    "skills": 0.30,
    "experience": 0.30
}

def score_job_applicant(resume):
    job = resume.job

    # You can replace job.description with actual structured fields if available
    job_requirements = {
        "qualifications": job.qualifications_required or "",
        "skills": job.skills_required or "",
        "experience": job.experience_required or ""
    }

    applicant_data = {
        "qualifications": resume.qualifications or "",
        "skills": " ".join(resume.skills) if isinstance(resume.skills, list) else resume.skills or "",
        "experience": resume.experience or ""
    }

    # Score calculation
    details = {}
    total_score = 0.0

    for category, weight in weights.items():
        raw_score = fuzz.token_sort_ratio(job_requirements[category], applicant_data[category])
        weighted_score = raw_score * weight
        details[category] = round(raw_score, 2)
        total_score += weighted_score

    total_score = round(total_score, 2)

    # Updated match labels based on thesis
    if total_score >= 85:
        job_match = "Highly Qualified"
    elif total_score >= 70:
        job_match = "Qualified"
    elif total_score >= 50:
        job_match = "Moderately Qualified"
    else:
        job_match = "Not Qualified"

    return {
        "final_score": total_score,
        "job_match": job_match,
        "details": details
    }

def score_job_applicant(resume):
    from rapidfuzz import fuzz

    job = resume.job
    weights = {
        "qualifications": 0.40,
        "skills": 0.30,
        "experience": 0.30
    }

    job_requirements = {
        "qualifications": job.qualifications_required or "",
        "skills": job.skills_required or "",
        "experience": job.experience_required or ""
    }

    applicant_data = {
        "qualifications": resume.qualifications or "",
        "skills": " ".join(resume.skills) if isinstance(resume.skills, list) else resume.skills or "",
        "experience": resume.experience or ""
    }

    # Base fuzzy match scoring
    details = {}
    total_score = 0.0
    for category, weight in weights.items():
        raw_score = fuzz.token_sort_ratio(job_requirements[category], applicant_data[category])
        weighted_score = raw_score * weight
        details[category] = round(raw_score, 2)
        total_score += weighted_score

    # Faculty Rank Matrix Boosts
    education_score = 0
    training_score = 0
    eligibility_score = 0

    # Education match (Master’s Degree assumed ideal)
    if "master" in resume.qualifications.lower():
        education_score = 10

    # Experience years (simple heuristic)
    experience_years = extract_years_from_experience(resume.experience)
    if experience_years >= 5:
        training_score = 10
    elif experience_years >= 3:
        training_score = 7
    elif experience_years >= 1:
        training_score = 4

    # Training hours (numeric field)
    if resume.training_hours >= 32:
        training_score += 10
    elif resume.training_hours >= 16:
        training_score += 7
    elif resume.training_hours >= 4:
        training_score += 4

    # Eligibility (RA 1080)
    if "ra 1080" in resume.eligibility.lower():
        eligibility_score = 5

    # Adjust total score with matrix components
    matrix_score = education_score + training_score + eligibility_score
    final_score = round(total_score + matrix_score, 2)

    # Classification
    if final_score >= 85:
        job_match = "Highly Qualified"
    elif final_score >= 70:
        job_match = "Qualified"
    elif final_score >= 50:
        job_match = "Moderately Qualified"
    else:
        job_match = "Not Qualified"

    return {
        "final_score": final_score,
        "job_match": job_match,
        "details": {
            **details,
            "education_matrix": education_score,
            "training_matrix": training_score,
            "eligibility_matrix": eligibility_score
        }
    }

import re

def extract_years_from_experience(text):
    try:
        matches = re.findall(r"(\d+)\+?\s*year", text.lower())
        years = [int(m) for m in matches]
        return max(years) if years else 0
    except:
        return 0
