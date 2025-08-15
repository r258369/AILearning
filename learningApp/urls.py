from django.contrib import admin
from django.urls import path
from learningApp import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('onboarding-quiz/', views.onboarding_quiz_view, name='onboarding_quiz'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('lesson/', views.lesson_view, name='lesson'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('notes/', views.notes_view, name='notes'),
    path('settings-feedback/', views.settings_feedback_view, name='settings_feedback'),
    path('syllabus/', views.syllabus_view, name='syllabus'), # New syllabus page
    #path('classroom/auth/', views.classroom_auth, name='classroom_auth'), # Removed as classroom_auth is no longer used
    path('logout/', views.logout_view, name='logout'),
    path('mark-video-complete/', views.mark_video_complete, name='mark_video_complete'),
    path('generate-study-notes/', views.generate_study_notes, name='generate_study_notes'),
    #path('generate-syllabus/', views.generate_syllabus_view, name='generate-syllabus'),
]
