from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Job, Application, User, Profile, ResumeApplication
from datetime import datetime
# from .forms import RegisterForm, CustomLoginForm, ApplicationForm


def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif not role:
            messages.error(request, "Please select a role.")
        else:
            # ✅ FIX: delay saving to inject role BEFORE save
            user = User(username=username, email=email)
            user.set_password(password)
            user._role = role  # temporary attribute for signal
            user.save()        # signal will now see _role
            login(request, user)

            if role == 'employer':
                return redirect('employer_dashboard')
            else:
                return redirect('seeker_dashboard')

    return render(request, 'register.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role = user.profile.role
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if role == 'employer':
                return redirect('employer_dashboard')
            else:
                return redirect('seeker_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def seeker_dashboard(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Create a profile if it doesn't exist (e.g., for older users)
        # Defaulting to 'seeker' role
        profile = Profile.objects.create(user=request.user, role='seeker')

    if profile.role != 'seeker':
        # Redirect non-seekers (e.g., employers) appropriately
        messages.error(request, "Access denied.")
        return redirect('home') # Or another appropriate URL

    # Fetch applications for the logged-in seeker
    applications = Application.objects.filter(user=request.user).select_related('job').order_by('-application_date')

    context = {
        'user': request.user,
        'profile': profile,
        'applications': applications,
    }
    return render(request, 'seeker_dashboard.html', context)

def job_list(request):
    jobs = Job.objects.all()  # You can add filters here to show specific jobs
    return render(request, 'job_list.html', {'jobs': jobs})

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {'job': job})


@login_required # Ensure user is logged in to apply
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if the user has already applied using the standard Application model
    if Application.objects.filter(user=request.user, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        # Collect fixed fields from POST data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        title = request.POST.get('title') # Applicant's professional title
        objective = request.POST.get('objective')

        # --- Parse Experience --- 
        experience_titles = request.POST.getlist('experience_title[]')
        experience_companies = request.POST.getlist('experience_company[]')
        experience_locations = request.POST.getlist('experience_location[]')
        experience_durations = request.POST.getlist('experience_duration[]') # Changed from start/end dates
        experience_employment_types = request.POST.getlist('experience_employment_type[]') # Added
        experience_descriptions = request.POST.getlist('experience_description[]')

        experiences = []
        for i in range(len(experience_titles)):
            experiences.append({
                'title': experience_titles[i],
                'company': experience_companies[i],
                'location': experience_locations[i] if i < len(experience_locations) else '',
                'duration': experience_durations[i] if i < len(experience_durations) else '', # Use duration
                'employment_type': experience_employment_types[i] if i < len(experience_employment_types) else '', # Add employment type
                'description': experience_descriptions[i],
            })

        # --- Parse Education --- 
        institutions = request.POST.getlist('education_institution[]')
        addresses = request.POST.getlist('education_address[]') # Added
        courses = request.POST.getlist('education_course[]') # Changed from degree
        years = request.POST.getlist('education_year[]')
        # education_details = request.POST.getlist('education_details[]') # Removed, not in form

        education = []
        for i in range(len(institutions)):
            education.append({
                'institution': institutions[i],
                'address': addresses[i] if i < len(addresses) else '', # Add address
                'course': courses[i] if i < len(courses) else '', # Use course
                'year': years[i] if i < len(years) else '', # Use year range
                # 'details': education_details[i] if i < len(education_details) else '', # Removed
            })

        # --- Parse Skills --- 
        skills = request.POST.getlist('skill_name[]')

        # --- Parse Seminars --- 
        seminar_titles = request.POST.getlist('seminar_title[]')
        seminar_organizers = request.POST.getlist('seminar_organizer[]')
        seminar_dates = request.POST.getlist('seminar_date[]')

        seminars = []
        for i in range(len(seminar_titles)):
            seminars.append({
                'title': seminar_titles[i],
                'organizer': seminar_organizers[i] if i < len(seminar_organizers) else '',
                'date': seminar_dates[i] if i < len(seminar_dates) else '',
            })

        # --- Parse References --- 
        reference_names = request.POST.getlist('reference_name[]')
        reference_positions = request.POST.getlist('reference_position[]')
        reference_companies = request.POST.getlist('reference_company[]')
        reference_contacts = request.POST.getlist('reference_contact[]')

        references = []
        for i in range(len(reference_names)):
            references.append({
                'name': reference_names[i],
                'position': reference_positions[i] if i < len(reference_positions) else '',
                'company': reference_companies[i] if i < len(reference_companies) else '',
                'contact': reference_contacts[i] if i < len(reference_contacts) else '',
            })

        # Save the detailed resume application
        resume_app = ResumeApplication.objects.create(
            job=job,
            name=name,
            email=email,
            phone=phone,
            location=location,
            title=title,
            objective=objective,
            experiences=experiences,
            education=education,
            skills=skills,
            seminars=seminars, # Add seminars
            references=references, # Add references
        )

        # Trigger the scoring process
        try:
            resume_app.compute_score()
        except Exception as e:
            # Log the error or handle it appropriately
            # This prevents scoring errors from breaking the application process
            print(f"Error computing score for application {resume_app.id}: {e}") 

        # ALSO create the standard Application record linking user and job
        try:
            Application.objects.create(
                user=request.user,
                job=job,
            )
            messages.success(request, "Your application was submitted successfully!")
        except IntegrityError: # Catch potential unique_together constraint violation
             messages.warning(request, "You have already applied for this job (concurrent request).")
             resume_app.delete()
             return redirect('job_detail', job_id=job.id)

        return redirect('seeker_dashboard') # Redirect to dashboard to see the application

    # If GET request, render the form
    return render(request, 'apply_to_job.html', {'job': job})

@login_required
def employer_dashboard(request):
    # Check if user has a profile and if role is employer
    try:
        profile = request.user.profile
        if profile.role != 'employer':
            messages.error(request, "Access denied. This dashboard is for employers only.")
            return redirect('home')
    except Profile.DoesNotExist:
        # Create a profile if it doesn't exist (should be rare due to signals)
        profile = Profile.objects.create(user=request.user, role='employer')
    
    # Fetch jobs posted by the current employer (user) with their application counts
    jobs = Job.objects.filter(posted_by=request.user).order_by('-date_posted')
    
    # Add application count to each job
    for job in jobs:
        job.application_count = ResumeApplication.objects.filter(job=job).count()
        job.recent_applications = ResumeApplication.objects.filter(job=job).order_by('-id')[:5]
    
    # Get recent applications across all jobs (limited to 10)
    recent_applications = ResumeApplication.objects.filter(
        job__in=jobs
    ).select_related('job').order_by('-id')[:10]
    
    # Get total applications count
    total_applications_count = ResumeApplication.objects.filter(job__in=jobs).count()
    
    # Get active and inactive job counts
    # Assuming you might want to add a 'status' field to Job model in the future
    active_jobs_count = jobs.count()
    
    context = {
        'user': request.user,
        'profile': profile,
        'jobs': jobs,
        'recent_applications': recent_applications,
        'total_jobs': jobs.count(),
        'total_applications': total_applications_count,
        'active_jobs': active_jobs_count,
        'page_title': 'Employer Dashboard',
    }
    
    return render(request, 'employer_dashboard.html', context)

@login_required
def create_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        company_name = request.user.username  # or use a company profile if you have one

        Job.objects.create(
            title=title,
            description=description,
            location=location,
            company_name=company_name,
            posted_by=request.user
        )
        return redirect('employer_dashboard')
    return render(request, 'create_job.html')

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.location = request.POST.get('location')
        job.save()
        return redirect('employer_dashboard')

    return render(request, 'edit_job.html', {'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)

    if request.method == 'POST':
        job.delete()
        return redirect('employer_dashboard')

    return render(request, 'delete_job.html', {'job': job})


def view_application(request, application_id):
    # Fetch the detailed ResumeApplication object
    application = get_object_or_404(ResumeApplication, id=application_id)

    # Prepare context data matching the template's variable names,
    # using the actual data stored in the ResumeApplication model.
    context_data = {
        'application': application, # Pass the whole object for potential use
        'name': application.name,
        'title': application.title, # Professional Title from application
        'objective': application.objective,
        'contact_info': {
            'location': application.location,
            'phone': application.phone,
            'email': application.email,
        },
        'experience': application.experiences or [], # Pass the list directly
        'education': application.education or [],   # Pass the list directly
        'skills': application.skills or [],       # Pass the list directly
        'trainings': application.seminars or [],    # Map model's 'seminars' to template's 'trainings'
        'references': application.references or [], # Pass the list directly
    }

    # Render the template with the application data
    return render(request, 'view_application.html', context_data)


@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Fetch all applications with their related scores
    applicants = ResumeApplication.objects.filter(job=job).select_related('score')

    # Optional: sort applicants by score if available
    sorted_applicants = sorted(
        applicants,
        key=lambda a: a.score.final_score if hasattr(a, 'score') and a.score else 0,
        reverse=True
    )

    context = {
        'job': job,
        'applicants': sorted_applicants,
    }
    return render(request, 'view_applicants.html', context)

def view_score_details(request, application_id):
    """
    View detailed score breakdown for a specific application with comparison to other applicants
    """
    application = get_object_or_404(ResumeApplication, id=application_id)
    
    # Check if the user is authorized (employer who posted the job)
    if not request.user.is_authenticated:
        return redirect('login')
        
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'employer' or application.job.posted_by != request.user:
        messages.error(request, "You don't have permission to view this application's score.")
        return redirect('seeker_dashboard')
    
    # Check if score exists for this application
    if not hasattr(application, 'score'):
        # Try to compute the score if it doesn't exist
        try:
            application.compute_score()
            messages.success(request, "Score has been calculated successfully.")
        except Exception as e:
            messages.warning(request, f"Could not calculate score for this application: {str(e)}")
            return redirect('view_application', application_id=application_id)
    
    # Get job-related information for context
    job = application.job
    
    # Get statistics for comparison
    all_scores = []
    job_level_scores = []
    
    # Get all applications for this job with scores
    job_applications = ResumeApplication.objects.filter(job=job).select_related('score')
    valid_applications = [app for app in job_applications if hasattr(app, 'score') and app.score]
    
    if valid_applications:
        # Calculate average and highest scores for comparison
        all_scores = [app.score.final_score for app in valid_applications]
        avg_score = sum(all_scores) / len(all_scores)
        highest_score = max(all_scores) if all_scores else 0
        
        # Calculate statistics for applications with same job match level
        job_level = application.score.job_match if hasattr(application, 'score') else None
        if job_level:
            job_level_apps = [app for app in valid_applications 
                              if app.score.job_match == job_level]
            job_level_scores = [app.score.final_score for app in job_level_apps]
            avg_level_score = sum(job_level_scores) / len(job_level_scores) if job_level_scores else 0
            highest_level_score = max(job_level_scores) if job_level_scores else 0
            rank_in_level = sorted(job_level_scores, reverse=True).index(application.score.final_score) + 1 if application.score else 0
        else:
            avg_level_score = 0
            highest_level_score = 0
            rank_in_level = 0
        
        # Calculate overall rank
        rank_overall = sorted(all_scores, reverse=True).index(application.score.final_score) + 1 if application.score else 0
    else:
        avg_score = 0
        highest_score = 0
        avg_level_score = 0
        highest_level_score = 0
        rank_overall = 1
        rank_in_level = 1
    
    context = {
        'application': application,
        'job': job,
        'stats': {
            'total_applicants': len(valid_applications),
            'avg_score': round(avg_score, 2),
            'highest_score': round(highest_score, 2),
            'avg_level_score': round(avg_level_score, 2),
            'highest_level_score': round(highest_level_score, 2),
            'rank_overall': rank_overall,
            'rank_in_level': rank_in_level,
            'percentile': round(100 * (1 - (rank_overall - 1) / len(valid_applications))) if len(valid_applications) > 1 else 100
        }
    }
    
    # Add action parameter if provided (e.g., for rescoring)
    if request.GET.get('action') == 'rescore':
        try:
            application.compute_score()
            messages.success(request, "Application has been rescored successfully.")
        except Exception as e:
            messages.error(request, f"Error rescoring application: {str(e)}")
    
    return render(request, 'score_detail.html', context)