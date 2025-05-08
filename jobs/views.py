from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Job, Application, User, Profile, ResumeApplication
from datetime import datetime
import json
import ast
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
@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if Application.objects.filter(user=request.user, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        title = request.POST.get('title')

        qualifications = request.POST.get('qualifications')
        experience = request.POST.get('experience')

        # 🧠 NEW: Clean skill input
        skills_raw = request.POST.get('skills', '')
        skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]  # from comma-separated string

        resume_app = ResumeApplication.objects.create(
            job=job,
            name=name,
            email=email,
            phone=phone,
            location=location,
            title=title,
            qualifications=qualifications,
            experience=experience,
            skills=skills_list,  # ✅ stores as list in JSONField
        )

        try:
            resume_app.compute_score()
        except Exception as e:
            print(f"[ERROR] compute_score failed: {e}")

        try:
            Application.objects.create(
                user=request.user,
                job=job
            )
            messages.success(request, "Application submitted successfully.")
        except IntegrityError:
            messages.warning(request, "Concurrent submission detected.")
            resume_app.delete()
            return redirect('job_detail', job_id=job.id)

        return redirect('seeker_dashboard')

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
    jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_date')
    
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
        company_name = request.user.username  # or company profile if separate

        qualifications = request.POST.get('qualifications_required')
        skills = request.POST.get('skills_required')
        experience = request.POST.get('experience_required')

        Job.objects.create(
            title=title,
            description=description,
            location=location,
            company_name=company_name,
            posted_by=request.user,
            qualifications_required=qualifications,
            skills_required=skills,
            experience_required=experience
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
        job.qualifications_required = request.POST.get('qualifications_required')
        job.skills_required = request.POST.get('skills_required')
        job.experience_required = request.POST.get('experience_required')
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
    application = get_object_or_404(ResumeApplication, id=application_id)

    context = {
        'application': application,
        'name': application.name,
        'title': application.title,
        'contact_info': {
            'location': application.location,
            'phone': application.phone,
            'email': application.email,
        },
        'objective': application.objective or "No objective provided.",
        'experience': application.experiences or "No work experience provided.",
        'education': application.education or "No educational background provided.",
        'skills': application.skills or [],
    }

    return render(request, 'view_application.html', context)


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
    application = get_object_or_404(ResumeApplication, id=application_id)

    # Authorization check
    if request.user.profile.role != 'employer' or application.job.posted_by != request.user:
        messages.error(request, "You don't have permission to view this score.")
        return redirect('seeker_dashboard')

    # Score check
    if not hasattr(application, 'score'):
        try:
            application.compute_score()
            messages.success(request, "Score calculated.")
        except Exception as e:
            messages.warning(request, f"Score calculation failed: {e}")
            return redirect('view_application', application_id=application_id)

    job = application.job
    job_apps = ResumeApplication.objects.filter(job=job).select_related('score')
    valid_apps = [a for a in job_apps if hasattr(a, 'score') and a.score]

    stats = {
        'total_applicants': len(valid_apps),
        'avg_score': 0,
        'avg_level_score': 0,
        'highest_score': 0,
        'highest_level_score': 0,
        'rank_overall': 1,
        'rank_in_level': 1,
        'percentile': 100
    }

    if valid_apps:
        scores = [a.score.final_score for a in valid_apps]
        stats['avg_score'] = sum(scores) / len(scores)
        stats['highest_score'] = max(scores)

        level = application.score.job_match
        same_level = [a.score.final_score for a in valid_apps if a.score.job_match == level]
        stats['avg_level_score'] = sum(same_level) / len(same_level) if same_level else 0
        stats['highest_level_score'] = max(same_level) if same_level else 0

        stats['rank_overall'] = sorted(scores, reverse=True).index(application.score.final_score) + 1
        stats['rank_in_level'] = sorted(same_level, reverse=True).index(application.score.final_score) + 1 if same_level else 1

        stats['percentile'] = round(100 * (1 - ((stats['rank_overall'] - 1) / len(valid_apps))))

    return render(request, 'score_detail.html', {
        'application': application,
        'job': job,
        'stats': stats
    })