from django.contrib import admin
from .models import Job, Application, Profile, ResumeApplication, ResumeScore

# Register your models here.

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Profile)
admin.site.register(ResumeApplication)
admin.site.register(ResumeScore)