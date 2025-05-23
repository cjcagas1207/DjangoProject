# Generated by Django 5.2.1 on 2025-05-08 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_rename_objective_resumeapplication_experience_and_more'),
    ]

    operations = [
        # 1) Coerce any existing non-JSON or NULL skills into an empty list
        migrations.RunSQL(
            sql="""
                UPDATE jobs_resumeapplication
                SET skills = '[]'
                WHERE skills IS NULL
                   OR JSON_VALID(skills) = 0;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 2) Add the new fields
        migrations.AddField(
            model_name='resumeapplication',
            name='education',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='resumeapplication',
            name='experiences',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='resumeapplication',
            name='objective',
            field=models.TextField(blank=True, null=True),
        ),

        # 3) Now that all existing rows have valid JSON in `skills`,
        #    we can safely turn it into JSONField.
        migrations.AlterField(
            model_name='resumeapplication',
            name='skills',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
