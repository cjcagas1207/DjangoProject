from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = (
        ('employer', 'Job Employer'),
        ('seeker', 'Job Seeker'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    posted_date = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    qualifications_required = models.TextField(blank=True)
    skills_required = models.TextField(blank=True)
    experience_required = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('viewed', 'Viewed'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class ResumeApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    qualifications = models.TextField()
    experience = models.TextField()
    objective = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    experiences = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    training_hours = models.IntegerField(default=0)  # Added training_hours field
    eligibility = models.TextField(blank=True, default='')  # Also adding eligibility which appears to be used in scoring.py

    def compute_score(self):
        from jobs.utils.scoring import score_job_applicant
        result = score_job_applicant(self)
        ResumeScore.objects.update_or_create(
            resume=self,
            defaults={
                'job_match': result['job_match'],
                'final_score': result['final_score'],
                'qualifications_score': result['details'].get('qualifications', 0),
                'skills_score': result['details'].get('skills', 0),
                'experience_score': result['details'].get('experience', 0),
            }
        )

    def __str__(self):
        return f"{self.name} - {self.job.title}"


class ResumeScore(models.Model):
    resume = models.OneToOneField(ResumeApplication, on_delete=models.CASCADE, related_name='score')
    job_match = models.CharField(max_length=100)
    qualifications_score = models.FloatField(default=0.0)
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)
    computed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score for {self.resume.name} - {self.final_score:.2f}"
