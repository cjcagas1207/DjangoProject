# models.py
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
    date_posted = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)  # employer

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
    objective = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    experiences = models.JSONField()
    education = models.JSONField()
    skills = models.JSONField(blank=True, default=list)
    seminars = models.JSONField(blank=True, default=list)
    references = models.JSONField(blank=True, default=list)

    def compute_score(self):
        from .utils.scoring import score_job_applicant
        from .models import ResumeScore
        # Simplified debug version for clarity
        result = score_job_applicant(self)
        ResumeScore.objects.update_or_create(
            resume=self,
            defaults=result
        )

    def __str__(self):
        return f"{self.name} - {self.job.title}"


class ResumeScore(models.Model):
    resume = models.OneToOneField(ResumeApplication, on_delete=models.CASCADE, related_name='score')
    job_match = models.CharField(max_length=100)

    aspiration_motivational = models.FloatField(default=0.0)
    aspiration_behavioral = models.FloatField(default=0.0)
    ability_competency = models.FloatField(default=0.0)
    ability_learning = models.FloatField(default=0.0)
    engagement = models.FloatField(default=0.0)

    aspiration_score = models.FloatField(default=0.0)
    ability_score = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    aea_total = models.FloatField(default=0.0)

    education_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)

    effective_aspiration_max = models.FloatField(default=30.0)
    effective_ability_max = models.FloatField(default=30.0)
    effective_engagement_max = models.FloatField(default=30.0)
    effective_aea_max = models.FloatField(default=90.0)
    effective_total_max = models.FloatField(default=105.0)

    computed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score for {self.resume.name} - {self.final_score}"