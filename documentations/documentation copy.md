# Job Application and Scoring System Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [User Roles](#user-roles)
4. [Application Process](#application-process)
5. [Resume Structure](#resume-structure)
6. [Scoring System](#scoring-system)
7. [Views and Templates](#views-and-templates)
8. [Database Models](#database-models)
9. [Implementation Guide](#implementation-guide)

## Overview

The Job Application and Scoring System is a Django-based web application that allows job seekers to apply for positions and employers to evaluate applicants using a sophisticated scoring algorithm. The system stores detailed resume information and calculates scores based on job requirements, candidate qualifications, and a proprietary AEA (Aspiration, Engagement, Ability) framework.

## System Architecture

The application follows a standard Django MVT (Model-View-Template) architecture:

1. **Models** - Store job listings, user profiles, applications, and scoring data
2. **Views** - Handle user interactions, form submissions, and page rendering
3. **Templates** - Render UI components for users
4. **URLs** - Map routes to appropriate views

```
DjangoProject/
├── jobs/
│   ├── models.py      # Database models
│   ├── views.py       # View functions
│   ├── urls.py        # URL mappings
│   ├── templates/     # HTML templates
│   ├── static/        # CSS, JS, images
│   └── signals.py     # Model signals
├── manage.py          # Django command-line utility
└── DjangoProject/     # Project settings
    └── settings.py    # Project configuration
```

## User Roles

The system supports two main user roles:

1. **Job Seekers**
   - Register and create profiles
   - Browse available job listings
   - Submit detailed resume applications
   - Track application status

2. **Employers**
   - Post job listings with requirements
   - View submitted applications
   - Access detailed scoring for each applicant
   - Compare applicants via scoring metrics

## Application Process

The job application process follows these steps:

1. **Job Posting**: Employer creates a job listing with title, description, location, and qualifications
2. **Job Discovery**: Job seekers browse or search for jobs
3. **Application**: Job seeker completes the application form with detailed resume information
4. **Submission**: Application is stored and immediately scored against the job requirements
5. **Review**: Employer receives notification of new application and can view the resume and score
6. **Decision**: Employer uses score and resume information to make hiring decisions

## Resume Structure

The resume application form captures comprehensive candidate information:

1. **Personal Information**
   - Full name, professional title, contact info
   - Career objective

2. **Experience**
   - Job titles and companies
   - Employment dates and locations
   - Detailed job descriptions

3. **Education**
   - Institutions and locations
   - Degrees/courses and graduation years

4. **Skills**
   - Technical and soft skills

5. **Seminars & Training**
   - Professional development activities
   - Organizers and dates

6. **References**
   - Professional references and contact information

## Scoring System

### Scoring Framework

The scoring system evaluates candidates using a proprietary AEA framework:

1. **Aspiration** (30 points)
   - A1.1 Motivational Drivers (15 points)
   - A1.2 Behavioral Indicators (15 points)

2. **Ability** (30 points)
   - A2.1 Competency Demonstration (15 points)
   - A2.2 Learning Ability (15 points)

3. **Engagement** (15 points)
   - A3.1 Current + Future Engagement (15 points)

4. **Education & Experience** (15 points)
   - Education Score (7.5 points)
   - Experience Score (7.5 points)

### Job Match Categories

Applications are categorized by job match level:
- **Instructor I** - Entry-level teaching positions
- **Instructor II** - Mid-level positions requiring more experience
- **Instructor III** - Senior positions requiring extensive experience and expertise

### Calculation Algorithm

The system calculates scores through the following process:
1. Parse resume text and identify relevant keywords and qualifications
2. Compare qualifications against job requirements
3. Calculate sub-scores for each category
4. Apply weights based on job match level
5. Generate final score and percentages

## Views and Templates

### Key Templates

1. **apply_to_job.html**
   - Dynamic form for resume submission
   - Multiple sections for different resume components
   - JavaScript for adding additional entries

2. **view_application.html**
   - Detailed resume view for employers
   - Summary of applicant information
   - Link to score details

3. **score_detail.html**
   - Comprehensive scoring breakdown
   - Comparative statistics with other applicants
   - Visual indicators of strengths and weaknesses

4. **view_applicants.html**
   - Table of all applicants for a job
   - Summary scores with color coding
   - Links to detailed views

### Key Views

1. **apply_to_job(request, job_id)**
   - Handles resume form submission
   - Creates ResumeApplication record
   - Triggers score calculation

2. **view_application(request, application_id)**
   - Displays detailed resume for employers
   - Formats data for template rendering

3. **view_score_details(request, application_id)**
   - Displays detailed scoring breakdown
   - Calculates comparative statistics
   - Handles score recalculation requests

4. **view_applicants(request, job_id)**
   - Shows all applicants for a specific job
   - Sorts by score for easy comparison

## Database Models

### Core Models

1. **User & Profile**
   - Django's built-in User model
   - Extended Profile with role (employer/seeker)

2. **Job**
   - Basic job listing information
   - Posted by (employer reference)
   - Location, title, description

3. **Application**
   - Basic record linking User and Job
   - Application date

4. **ResumeApplication**
   - Detailed resume information
   - JSON fields for structured data (experiences, education, etc.)
   - Foreign key to Job

5. **Score**
   - One-to-one relationship with ResumeApplication
   - Detailed scoring components
   - Final score calculations

## Implementation Guide

### Setting Up a New Job

1. Log in as an employer
2. Navigate to employer dashboard
3. Click "Create New Job"
4. Enter job title, description, location, and requirements
5. Submit to publish the job

### Applying for a Job

1. Log in as a job seeker
2. Browse available jobs
3. Select a job and click "Apply"
4. Fill out the detailed resume form
5. Submit application

### Viewing and Scoring Applications

1. Log in as an employer
2. Navigate to employer dashboard
3. Select a job to view applicants
4. View the list of applicants with their scores
5. Click on individual applicants to view detailed resumes
6. Click "View Score" to see detailed scoring breakdown

### Recalculating Scores

1. Navigate to a score detail page
2. Click "Recalculate Score" button
3. System will reprocess the application and update scores

## Score Interpretation

- **80-90 points**: Excellent match for the position
- **60-79 points**: Good match with some development areas
- **Below 60 points**: Not an ideal match for this role

## Conclusion

This documentation provides a comprehensive overview of the Job Application and Scoring System. For further technical details, refer to the code comments within each file. The system is designed to be extensible, allowing for additional features and scoring criteria to be added as needed.