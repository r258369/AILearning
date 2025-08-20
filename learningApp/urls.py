from django.contrib import admin
from django.urls import path
from learningApp import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('onboarding-quiz/', views.onboarding_quiz_view, name='onboarding_quiz'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('lesson/', views.lesson_view, name='lesson'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('notes/', views.notes_view, name='notes'),
    path('settings-feedback/', views.settings_feedback_view, name='settings_feedback'),
    path('syllabus/', views.syllabus_view, name='syllabus'), # New syllabus page
    path('logout/', views.logout_view, name='logout'),
    path('mark-video-complete/', views.mark_video_complete, name='mark_video_complete'),
    path('generate-study-notes/', views.generate_study_notes, name='generate_study_notes'),
    path('generate-videos/', views.generate_videos_view, name='generate_videos'),
    path('clear-cache/', views.clear_user_cache, name='clear_cache'),
    path('test-gemini/', views.test_gemini_connection, name='test_gemini'),
    #path('generate-syllabus/', views.generate_syllabus_view, name='generate-syllabus'),
]
