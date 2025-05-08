# Developer Guide: Job Application & Scoring System

## Technical Architecture

### Project Structure
```
DjangoProject/
├── jobs/
│   ├── models.py      # Database models
│   ├── views.py       # View functions
│   ├── forms.py       # Form classes
│   ├── scoring.py     # Scoring algorithm
│   ├── urls.py        # URL patterns
│   ├── templates/     # HTML templates
│   │   ├── apply_to_job.html
│   │   ├── view_application.html
│   │   ├── score_detail.html
│   │   └── view_applicants.html
│   ├── static/        # CSS, JS, images
│   ├── signals.py     # Model signals
│   └── tests.py       # Unit tests
└── DjangoProject/     # Project directory
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## Core Models

### Job Model
```python
class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    requirements = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('job_detail', args=[str(self.id)])
```

### ResumeApplication Model
```python
class ResumeApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    title = models.CharField(max_length=100)  # Professional title
    location = models.CharField(max_length=100)
    objective = models.TextField()
    
    # JSON Fields for structured data
    experiences = models.JSONField()
    education = models.JSONField()
    skills = models.JSONField()
    seminars = models.JSONField()
    references = models.JSONField()
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.job.title}"
        
    def calculate_score(self):
        """Triggers score calculation and creates or updates Score object"""
        from jobs.scoring import calculate_application_score
        return calculate_application_score(self)
```

### Score Model
```python
class Score(models.Model):
    JOB_MATCH_CHOICES = [
        ('Instructor I', 'Instructor I'),
        ('Instructor II', 'Instructor II'),
        ('Instructor III', 'Instructor III'),
    ]
    
    application = models.OneToOneField(ResumeApplication, on_delete=models.CASCADE, related_name='score')
    
    # Aspiration scores (30 pts)
    aspiration_motivational = models.FloatField()  # 15 pts
    aspiration_behavioral = models.FloatField()    # 15 pts
    
    # Ability scores (30 pts)
    ability_competency = models.FloatField()       # 15 pts
    ability_learning = models.FloatField()         # 15 pts
    
    # Engagement score (15 pts)
    engagement = models.FloatField()               # 15 pts
    
    # Education & Experience scores (15 pts)
    education_score = models.FloatField()          # 7.5 pts
    experience_score = models.FloatField()         # 7.5 pts
    
    # Derived fields
    job_match = models.CharField(max_length=20, choices=JOB_MATCH_CHOICES)
    aspiration_score = models.FloatField()  # Aspiration total
    ability_score = models.FloatField()     # Ability total
    aea_total = models.FloatField()         # Aspiration + Ability + Engagement
    final_score = models.FloatField()       # Total score (0-90)
    
    # Maximum points tracking for percentage calculations
    effective_aspiration_max = models.FloatField(default=30.0)
    effective_ability_max = models.FloatField(default=30.0)
    effective_engagement_max = models.FloatField(default=15.0)
    effective_aea_max = models.FloatField(default=75.0)
    effective_total_max = models.FloatField(default=90.0)
    
    computed_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Score for {self.application.name}: {self.final_score}"
```

## Scoring Algorithm Implementation

The scoring system is implemented in `scoring.py` and follows these key functions:

### Main Scoring Function
```python
def calculate_application_score(application):
    """
    Main function to calculate and save application score
    
    Args:
        application (ResumeApplication): The application to score
        
    Returns:
        Score: The calculated Score object
    """
    # Create or get existing score object
    score, created = Score.objects.get_or_create(application=application)
    
    # Calculate component scores
    score.aspiration_motivational = calculate_aspiration_motivational(application)
    score.aspiration_behavioral = calculate_aspiration_behavioral(application)
    score.ability_competency = calculate_ability_competency(application)
    score.ability_learning = calculate_ability_learning(application)
    score.engagement = calculate_engagement(application)
    score.education_score = calculate_education_score(application)
    score.experience_score = calculate_experience_score(application)
    
    # Calculate aggregated scores
    score.aspiration_score = score.aspiration_motivational + score.aspiration_behavioral
    score.ability_score = score.ability_competency + score.ability_learning
    score.aea_total = score.aspiration_score + score.ability_score + score.engagement
    
    # Determine job match level
    score.job_match = determine_job_match(application, score)
    
    # Calculate final score
    score.final_score = (
        score.aspiration_score + 
        score.ability_score + 
        score.engagement +
        score.education_score + 
        score.experience_score
    )
    
    # Save and return
    score.save()
    return score
```

### Component Scoring Functions

Each scoring component has its own function that analyzes different aspects of the application:

```python
def calculate_aspiration_motivational(application):
    """Evaluates career objectives and motivational indicators"""
    # Implementation details
    
def calculate_aspiration_behavioral(application):
    """Assesses behavioral indicators from experiences"""
    # Implementation details
    
def calculate_ability_competency(application):
    """Evaluates demonstrated skills and competencies"""
    # Implementation details

def calculate_ability_learning(application):
    """Assesses learning ability and adaptability"""
    # Implementation details
    
def calculate_engagement(application):
    """Evaluates current and potential engagement"""
    # Implementation details
    
def calculate_education_score(application):
    """Scores educational qualifications"""
    # Implementation details
    
def calculate_experience_score(application):
    """Scores relevant experience"""
    # Implementation details

def determine_job_match(application, score):
    """Determines appropriate job level match based on scores"""
    # Implementation details
```

## Key Views Implementation

### Apply to Job View
```python
def apply_to_job(request, job_id):
    """Handle job application submission and processing"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if request.method == 'POST':
        # Process form data into structured format
        experiences = process_experience_data(request.POST)
        education = process_education_data(request.POST)
        skills = process_skills_data(request.POST)
        seminars = process_seminars_data(request.POST)
        references = process_references_data(request.POST)
        
        # Create application
        application = ResumeApplication(
            job=job,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            title=request.POST.get('title'),
            location=request.POST.get('location'),
            objective=request.POST.get('objective'),
            experiences=experiences,
            education=education,
            skills=skills,
            seminars=seminars,
            references=references,
        )
        application.save()
        
        # Calculate score
        application.calculate_score()
        
        # Redirect to success page
        return redirect('application_success', application_id=application.id)
    
    # GET request - show form
    return render(request, 'apply_to_job.html', {'job': job})
```

### View Score Details View
```python
def view_score_details(request, application_id):
    """Display detailed scoring breakdown with comparative stats"""
    application = get_object_or_404(ResumeApplication, id=application_id)
    
    # Check if we need to recalculate the score
    if request.GET.get('action') == 'rescore':
        application.calculate_score()
    
    # Ensure score exists
    if not hasattr(application, 'score'):
        application.calculate_score()
    
    # Get comparative statistics
    stats = {
        'total_applicants': ResumeApplication.objects.filter(job=application.job).count(),
        'avg_score': Score.objects.filter(application__job=application.job).aggregate(Avg('final_score'))['final_score__avg'] or 0,
        'avg_level_score': Score.objects.filter(
            application__job=application.job, 
            job_match=application.score.job_match
        ).aggregate(Avg('final_score'))['final_score__avg'] or 0,
        'highest_score': Score.objects.filter(application__job=application.job).aggregate(Max('final_score'))['final_score__max'] or 0,
    }
    
    # Calculate rankings
    all_scores = list(Score.objects.filter(application__job=application.job).order_by('-final_score').values_list('final_score', flat=True))
    level_scores = list(Score.objects.filter(
        application__job=application.job, 
        job_match=application.score.job_match
    ).order_by('-final_score').values_list('final_score', flat=True))
    
    # Find position in ordered list
    stats['rank_overall'] = all_scores.index(application.score.final_score) + 1 if application.score.final_score in all_scores else 0
    stats['rank_in_level'] = level_scores.index(application.score.final_score) + 1 if application.score.final_score in level_scores else 0
    
    # Calculate percentile if enough applicants
    if stats['total_applicants'] > 10:
        stats['percentile'] = round(((stats['total_applicants'] - stats['rank_overall']) / stats['total_applicants']) * 100)
    
    return render(request, 'score_detail.html', {
        'application': application,
        'stats': stats,
    })
```

## Data Processing Functions

### Processing Form Data
```python
def process_experience_data(post_data):
    """Process experience data from form submission into structured JSON"""
    experiences = []
    titles = post_data.getlist('experience_title[]')
    companies = post_data.getlist('experience_company[]')
    locations = post_data.getlist('experience_location[]')
    durations = post_data.getlist('experience_duration[]')
    empl_types = post_data.getlist('experience_employment_type[]')
    descriptions = post_data.getlist('experience_description[]')
    
    for i in range(len(titles)):
        if titles[i]:  # Only process non-empty entries
            experience = {
                'title': titles[i],
                'company': companies[i] if i < len(companies) else '',
                'location': locations[i] if i < len(locations) else '',
                'duration': durations[i] if i < len(durations) else '',
                'employment_type': empl_types[i] if i < len(empl_types) else '',
                'description': descriptions[i] if i < len(descriptions) else '',
            }
            experiences.append(experience)
    
    return experiences
```

Similar functions exist for processing education, skills, seminars, and references data.

## Extending the System

### Adding a New Scoring Component

To add a new scoring component:

1. Update the `Score` model to include the new component field(s)
2. Create a calculation function in `scoring.py`
3. Modify the `calculate_application_score` function to include the new component
4. Update templates to display the new component

Example - Adding a "Cultural Fit" component:

1. Add to Score model:
```python
# in models.py
class Score(models.Model):
    # ...existing fields
    cultural_fit = models.FloatField(default=0)  # New field
    # Update final_score calculation
```

2. Create calculation function:
```python
# in scoring.py
def calculate_cultural_fit(application):
    """Evaluate cultural fit based on application data"""
    score = 0
    
    # Implementation logic
    
    return score
```

3. Update main calculation function:
```python
def calculate_application_score(application):
    # ...existing code
    score.cultural_fit = calculate_cultural_fit(application)
    
    # Update final score calculation
    score.final_score = (
        score.aspiration_score + 
        score.ability_score + 
        score.engagement +
        score.education_score + 
        score.experience_score +
        score.cultural_fit
    )
    # ...rest of function
```

4. Update display template:
```html
<!-- in score_detail.html -->
<tr>
    <td colspan="2">Cultural Fit</td>
    <td>{{ application.score.cultural_fit|floatformat:1 }}</td>
    <!-- other cells -->
</tr>
```

### Customizing Job Match Criteria

To modify how job match levels are determined:

1. Edit the `determine_job_match` function in `scoring.py`:
```python
def determine_job_match(application, score):
    """Determines appropriate job level match based on scores"""
    total = score.final_score
    
    # Example logic - customize as needed
    if total >= 75:
        return "Instructor III"
    elif total >= 60:
        return "Instructor II"
    else:
        return "Instructor I"
```

## Testing

The system includes unit tests for core functionality:

```python
# in tests.py
class ScoringTests(TestCase):
    def setUp(self):
        # Create test job and application
        self.job = Job.objects.create(
            title='Test Instructor Position',
            description='Test description',
            requirements='Test requirements',
            posted_by=User.objects.create_user('testuser')
        )
        
        self.application = ResumeApplication.objects.create(
            job=self.job,
            name='Test Applicant',
            email='test@example.com',
            phone='555-1234',
            title='Instructor',
            location='Test Location',
            objective='Test objective',
            experiences=[{
                'title': 'Test Position',
                'company': 'Test Company',
                'location': 'Test City',
                'duration': '2020-2022',
                'employment_type': 'Full-time',
                'description': 'Test description with keywords teaching curriculum'
            }],
            education=[{
                'institution': 'Test University',
                'address': 'Test Address',
                'course': 'Education',
                'year': '2015-2019'
            }],
            skills=[{'name': 'Teaching'}, {'name': 'Curriculum Development'}],
            seminars=[{
                'title': 'Teaching Methods',
                'organizer': 'Education Conference',
                'date': 'March 2021'
            }],
            references=[{
                'name': 'Test Reference',
                'position': 'Professor',
                'company': 'Test University',
                'contact': 'reference@example.com'
            }]
        )
        
    def test_score_calculation(self):
        """Test that score calculation works"""
        score = self.application.calculate_score()
        
        # Assert score was created
        self.assertIsNotNone(score)
        
        # Test individual components calculated
        self.assertTrue(0 <= score.aspiration_motivational <= 15)
        self.assertTrue(0 <= score.aspiration_behavioral <= 15)
        self.assertTrue(0 <= score.ability_competency <= 15)
        self.assertTrue(0 <= score.ability_learning <= 15)
        self.assertTrue(0 <= score.engagement <= 15)
        self.assertTrue(0 <= score.education_score <= 7.5)
        self.assertTrue(0 <= score.experience_score <= 7.5)
        
        # Test aggregated scores
        self.assertEqual(
            score.aspiration_score, 
            score.aspiration_motivational + score.aspiration_behavioral
        )
        self.assertEqual(
            score.ability_score,
            score.ability_competency + score.ability_learning
        )
        self.assertEqual(
            score.aea_total,
            score.aspiration_score + score.ability_score + score.engagement
        )
        self.assertEqual(
            score.final_score,
            score.aspiration_score + score.ability_score + score.engagement + 
            score.education_score + score.experience_score
        )
        
        # Test job match assigned
        self.assertIn(score.job_match, ['Instructor I', 'Instructor II', 'Instructor III'])
```

## Deployment Notes

### Dependencies
- Django 4.1+
- Postgres (recommended for production)
- Python 3.8+

### Configuration

Key settings to configure:
- Database connection details in settings.py
- Email configuration for notifications
- Static file serving (use CDN in production)
- Session and cache settings for performance

### Performance Considerations

For large-scale deployments:
- Consider running score calculations asynchronously using Celery
- Implement database query optimizations and indexes
- Cache frequently accessed data (job listings, aggregate stats)
- Use pagination for applicant listings with many entries

## Security Considerations

The application implements several security measures:

1. **Input Validation**
   - Form validation for all input fields
   - Sanitization of user-provided content

2. **Access Control**
   - Role-based permissions (employer vs. applicant)
   - Object-level permissions (employers can only see their own job applications)

3. **Data Protection**
   - CSRF protection on all forms
   - Sensitive data encryption
   - SQL injection prevention through ORM

4. **Audit Trail**
   - Logging of scoring calculations
   - Timestamps on all application actions