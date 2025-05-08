from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('seeker/dashboard/', views.seeker_dashboard, name='seeker_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_to_job, name='apply_for_job'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/job/create/', views.create_job, name='create_job'),
    path('employer/job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('employer/job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('employer/application/<int:application_id>/view/', views.view_application, name='view_application'),
    path('employer/application/<int:application_id>/score/', views.view_score_details, name='view_score_details'),
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
]
