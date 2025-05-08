from django.db import migrations, models

def sanitize_skills(apps, schema_editor):
    ResumeApplication = apps.get_model('jobs', 'ResumeApplication')
    for app in ResumeApplication.objects.all():
        # if skills isn’t a proper JSON list, reset it
        try:
            # if it's a string, try parsing it
            if not isinstance(app.skills, list):
                models.JSONField().to_python(app.skills)
        except Exception:
            app.skills = []
            app.save()

class Migration(migrations.Migration):

    dependencies = [
        # <— change this to your actual last migration
        ('jobs', '0011_resumeapplication_education_and_more'),
    ]

    operations = [
        migrations.RunPython(sanitize_skills, reverse_code=migrations.RunPython.noop),
    ]
