from datetime import datetime
from bs4 import BeautifulSoup
# from googleapiclient.discovery import build  # Removed YouTube API import
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from .forms import UserProfileForm, SignupForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from firebase_config import db
from firebase_admin import firestore, auth
import google.generativeai as genai
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
import json
import wikipedia
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os
from firebase_admin import storage
import re
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import base64

import markdown
from weasyprint import HTML, CSS

genai.configure(api_key=settings.GEMINI_API_KEY)
#AIzaSyBXQvI2hY5j0bir7LhZP6-fjH_DABSViys
#AIzaSyCQytywPJB33ldrGwCqXFmtF4NnHTWsw3w

#Youtube api RH: AIzaSyAqPQ6uGc9pRSM2pizKh_jCCq4PH1RHbAg
#Youtube api RR: AIzaSyBjBuvcUMEqCX6fafa4KcF8pMzmEL-M49Q
#Youtube api Razi: AIzaSyCSPgqSCkFZWbm0jqHICgZCdH1KYFMGrFk

FIREBASE_WEB_API_KEY = "AIzaSyCs1UPbSV0LsooYerhIa9z_8j9nIqGYrP4" 
# YOUTUBE_API_KEY = "AIzaSyCSPgqSCkFZWbm0jqHICgZCdH1KYFMGrFk"  # Removed
# YOUTUBE_API_SERVICE_NAME = "youtube"  # Removed
# YOUTUBE_API_VERSION = "v3"  # Removed




# Channel mappings for different subjects
CHANNEL_IDS = {
    "Math": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],  # Khan Academy, 3Blue1Brown
    "Science": ["UCX6b17PVsYBQ0ip5gyeme-Q", "UCzF43z3REx3j4v4BIFyq_1Q"],  # CrashCourse, Amoeba Sisters
    "Physics": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],  # MinutePhysics, Physics Girl
    "Chemistry": ["UCj3EXpr5vF9x4eTnYFzfzIA"],  # Tyler DeWitt
    "Biology": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],  # Khan Academy, CrashCourse
    "Engineering": ["UCEBb1b_L6zDS3xTUrIALZOw"],  # MIT OpenCourseWare
    "Computer Science": [
        "UC8butISFwT-Wl7EV0hUK0BQ", 
        "UCW5YeuERMmlnqo4oq8vwUpg",
        "UCeVMnSShP_Iviwkknt83cww",
        "UCpRS3Dd6XDikYXYzKcozD2A"
    ],
}

# Topic-specific channel mappings for more precise video matching
TOPIC_CHANNEL_MAPPING = {
    # Math topics
    "algebra": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "calculus": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "geometry": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "trigonometry": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "statistics": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "probability": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "equation": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "function": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "derivative": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    "integral": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCYO_jab_esuFRV4b17AJtAw"],
    # Physics topics
    "mechanics": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "thermodynamics": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "electromagnetism": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "optics": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "quantum": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "force": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "energy": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "wave": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    "motion": ["UCUHW94eEFW7hkUMVaZz4eDg", "UC7DdEm33SyaTDtWYGO2CwdA"],
    # Chemistry topics
    "organic": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "inorganic": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "biochemistry": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "analytical": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "reaction": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "molecule": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "bond": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "acid": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    "base": ["UCj3EXpr5vF9x4eTnYFzfzIA"],
    # Biology topics
    "cell": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "genetics": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "evolution": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "ecology": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "dna": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "protein": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "enzyme": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    "photosynthesis": ["UC4a-Gbdw7vOaccHmFo40b9g", "UCX6b17PVsYBQ0ip5gyeme-Q"],
    # Computer Science topics
    "python": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "javascript": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "java": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "html": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "css": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "react": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "node": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "database": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "algorithm": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "data structure": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "programming": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "coding": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "web": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    "app": ["UC8butISFwT-Wl7EV0hUK0BQ", "UCW5YeuERMmlnqo4oq8vwUpg"],
    # Engineering topics
    "mechanical": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "electrical": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "civil": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "chemical": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "computer": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "circuit": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "design": ["UCEBb1b_L6zDS3xTUrIALZOw"],
    "system": ["UCEBb1b_L6zDS3xTUrIALZOw"],
}

def get_relevant_channels_for_topic(topic, preferred_subjects):
    topic_lower = topic.lower().strip()
    for topic_key, channels in TOPIC_CHANNEL_MAPPING.items():
        if topic_key in topic_lower:
            return channels
    for topic_key, channels in TOPIC_CHANNEL_MAPPING.items():
        if topic_key in topic_lower or topic_lower in topic_key:
            return channels
    subject_channels = []
    preferred_subjects_list = [s.strip() for s in preferred_subjects.split(',')]
    for subject in preferred_subjects_list:
        if subject in CHANNEL_IDS:
            subject_channels.extend(CHANNEL_IDS[subject])
    return list(set(subject_channels))

def generate_structured_content_with_gemini(topic, level,specific_goals):
    prompt = f'''
Specific Goals: {specific_goals}
Topic: {topic}\nLevel: {level}
1. Research and write clear, concise study notes (400-500 words, student-friendly tone, with relevant examples like maths, codes, etc.) using your internal knowledge and web search capabilities to gather accurate and up-to-date information from reliable public sources (e.g., Wikipedia, OpenStax, Khan Academy, Byju's, etc.).
2. Create a 5-question assignment (mix of MCQ, fill-in-the-blanks, and short answers) based on the notes. For MCQs, provide 4 options (a-d). For fill-in-the-blanks, indicate the blank with underscores. For short answers, ask questions that can be answered in 2-3 sentences.
Format for PDF:
📝 Study Notes
📄 Assignment Questions
'''
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error for {topic}: {e}")
        return ""

def parse_gemini_content_to_sections(gemini_text):
    # Simple parser to split the Gemini output into sections
    notes, assignment = "", ""
    lines = gemini_text.splitlines()
    section = None
    for line in lines:
        l = line.strip()
        if l.startswith("📝"):
            section = "notes"
            continue
        elif l.startswith("📄"):
            section = "assignment"
            continue
        if section == "notes":
            notes += line + "\n"
        elif section == "assignment":
            assignment += line + "\n"
    return {"notes": notes.strip(), "assignment": assignment.strip()}

def convert_text_to_html_for_pdf(topic, notes_content, assignment_content):
    notes_html = markdown.markdown(notes_content, extensions=['fenced_code', 'nl2br'])
    assignment_html = markdown.markdown(assignment_content, extensions=['fenced_code', 'nl2br'])

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{topic} Study Notes</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; line-height: 1.6; color: #333; }}
            h1, h2, h3 {{ color: #2563eb; margin-bottom: 10px; }}
            h1 {{ font-size: 1.6em; border-bottom: 2px solid #2563eb; padding-bottom: 5px; margin-bottom: 20px; }}
            h2 {{ font-size: 1.3em; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
            h3 {{ font-size: .9em; margin-top: 20px; }}
            p {{ margin-bottom: 10px; text-align: justify; }}
            ul, ol {{ margin-bottom: 10px; padding-left: 25px; }}
            li {{ margin-bottom: 5px; }}
            pre {{ background-color: #f4f4f4; border: 1px solid #ddd; padding: 10px; border-radius: 5px; overflow-x: auto; margin-bottom: 15px; }}
            code {{ font-family: 'Consolas', 'Courier New', monospace; background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
            .section-icon {{ font-size: .9em; margin-right: 8px; color: #10b981; }}
            .assignment-question {{ margin-bottom: 15px; border-left: 4px solid #f97316; padding-left: 10px; }}
            .page-break {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <h1>{topic} Study Notes</h1>

        <h2><span class="section-icon">📝</span> Study Notes</h2>
        <div>{notes}</div>

        <div class="page-break"></div>

        <h2><span class="section-icon">📄</span> Assignment Questions</h2>
        <div>{assignments}</div>
    </body>
    </html>
    """

    final_html = html_template.format(
        topic=topic,
        notes=notes_html,
        assignments=assignment_html
    )
    return final_html


def generate_pdf_from_content(content_dict, topic, user_id):
    try:
        # Convert content to HTML
        html_string = convert_text_to_html_for_pdf(
            topic,
            content_dict["notes"],
            content_dict["assignment"]
        )

        # Generate PDF using WeasyPrint
        # WeasyPrint can directly convert HTML string to PDF bytes
        pdf_bytes = HTML(string=html_string).write_pdf()

        # Encode to base64
        pdf_content_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        return f"data:application/pdf;base64,{pdf_content_base64}"

    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}")
        return None

def save_note_to_firestore(user_id, topic, pdf_content_base64, course_name):
    """
    Save study notes using Firestore subcollections to avoid document size limits.
    Structure: user_profiles/{user_id}/courses/{course_name}/notes/{topic}
    """
    if not pdf_content_base64:
        print(f"Failed to save PDF content for topic: {topic}")
        return False
    
    try:
        # Create a sanitized course name for use as document ID
        sanitized_course_name = re.sub(r'[^a-zA-Z0-9_-]', '_', course_name.lower())
        sanitized_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic.lower())
        
        # Create the course document reference
        course_ref = db.collection('user_profiles').document(user_id).collection('courses').document(sanitized_course_name)
        
        # Set course metadata (this document will be small)
        course_ref.set({
            'coursename': course_name,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_updated': firestore.SERVER_TIMESTAMP,
            'note_count': firestore.Increment(1)
        }, merge=True)
        
        # Create the note document in the course's notes subcollection
        note_ref = course_ref.collection('notes').document(sanitized_topic)
        
        # Save the note with metadata
        note_ref.set({
            'topic': topic,
            'pdf_content': pdf_content_base64,
            'created_at': firestore.SERVER_TIMESTAMP,
            'file_size_bytes': len(pdf_content_base64.encode('utf-8'))
        })
        
        print(f"PDF content saved to Firestore subcollection for topic: {topic} under course: {course_name}")
        return True
        
    except Exception as e:
        print(f"Error saving note to Firestore: {e}")
        return False


def get_notes_from_firestore(user_id):
    """
    Retrieve study notes from Firestore subcollections.
    Returns organized notes by course name.
    """
    try:
        organized_notes = {}
        
        # Get all courses for the user
        courses_ref = db.collection('user_profiles').document(user_id).collection('courses')
        courses = courses_ref.stream()
        
        for course_doc in courses:
            course_data = course_doc.to_dict()
            course_name = course_data.get('coursename', 'Untitled Course')
            
            # Get all notes for this course
            notes_ref = course_doc.reference.collection('notes')
            notes = notes_ref.stream()
            
            notes_list = []
            for note_doc in notes:
                note_data = note_doc.to_dict()
                notes_list.append({
                    'topic': note_data.get('topic', ''),
                    'pdf_url': note_data.get('pdf_content', ''),
                    'created_at': note_data.get('created_at'),
                    'file_size_bytes': note_data.get('file_size_bytes', 0)
                })
            
            # Sort notes by creation date (newest first)
            notes_list.sort(key=lambda x: x['created_at'] if x['created_at'] else '', reverse=True)
            organized_notes[course_name] = notes_list
        
        return organized_notes
        
    except Exception as e:
        print(f"Error retrieving notes from Firestore: {e}")
        return {}


def delete_note_from_firestore(user_id, course_name, topic):
    """
    Delete a specific note from Firestore subcollections.
    """
    try:
        sanitized_course_name = re.sub(r'[^a-zA-Z0-9_-]', '_', course_name.lower())
        sanitized_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic.lower())
        
        # Delete the note document
        note_ref = db.collection('user_profiles').document(user_id).collection('courses').document(sanitized_course_name).collection('notes').document(sanitized_topic)
        note_ref.delete()
        
        # Update course metadata
        course_ref = db.collection('user_profiles').document(user_id).collection('courses').document(sanitized_course_name)
        course_ref.update({
            'note_count': firestore.Increment(-1),
            'last_updated': firestore.SERVER_TIMESTAMP
        })
        
        print(f"Note deleted: {topic} from course: {course_name}")
        return True
        
    except Exception as e:
        print(f"Error deleting note from Firestore: {e}")
        return False


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

        response = requests.post(firebase_auth_url, data=payload)

        if response.status_code == 200:
            data = response.json()
            request.session['firebase_user'] = {
                'uid': data['localId'],
                'email': data['email'],
                'idToken': data['idToken'],
            }
            
            # Try to get user profile data to include name in session
            try:
                user_profile_ref = db.collection('user_profiles').document(data['localId'])
                user_profile_doc = user_profile_ref.get()
                if user_profile_doc.exists:
                    user_profile_data = user_profile_doc.to_dict()
                    request.session['firebase_user']['first_name'] = user_profile_data.get('first_name', '')
                    request.session['firebase_user']['last_name'] = user_profile_data.get('last_name', '')
            except Exception as e:
                print(f"Error fetching user profile for session: {e}")

            try:
                user, created = User.objects.get_or_create(username=data['localId'], defaults={'email': data['email']})
                if created:
                    user.set_unusable_password()
                    user.save()
                login(request, user)

            except Exception as e:
                messages.error(request, f"Error syncing Django user: {e}")
                return redirect('login')

            return redirect('dashboard') 
        else:
            error_message = response.json().get('error', {}).get('message', 'Login failed')
            messages.error(request, f"Login error: {error_message}")

    return render(request, 'login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():  
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            try:
                # Create user in Firebase Authentication
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=f"{first_name} {last_name}"
                )

                user_ref = db.collection('users').document(user.uid)
                user_ref.set({
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'created_at': firestore.SERVER_TIMESTAMP
                })

                user_profile_ref = db.collection('user_profiles').document(user.uid)
                user_profile_ref.set({
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'learning_style': '',
                    'preferred_subjects': '',
                    'skill_level': '',
                    'specific_goals': '',
                    'overall_progress': 0,
                    'lessons_completed': 0,
                    'average_quiz_score': 0,
                    'new_recommendations_count': 0,
                    'last_lesson_completed': '',
                    'last_quiz_taken': '',
                    'courses_progress': [],
                    'badges': [],
                    'last_updated': firestore.SERVER_TIMESTAMP
                })

               
                return redirect('login') 

            except Exception as e:

                form.add_error(None, str(e))
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def onboarding_quiz_view(request):
    # Using session to store quiz data across steps
    quiz_data = request.session.get('onboarding_quiz_data', {})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, initial=quiz_data)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                quiz_data[key] = value
            request.session['onboarding_quiz_data'] = quiz_data

            # Save to Firebase Firestore
            if request.user.is_authenticated:
                firebase_uid = request.session.get('firebase_user', {}).get('uid')
                if firebase_uid:
                    doc_ref = db.collection('user_profiles').document(firebase_uid)
                    doc_ref.set({
                        'learning_style': quiz_data.get('learning_style'),
                        'preferred_subjects': quiz_data.get('preferred_subjects'),
                        'skill_level': quiz_data.get('skill_level'),
                        'specific_goals': quiz_data.get('specific_goals'),
                        'last_updated': firestore.SERVER_TIMESTAMP
                    }, merge=True)

                    # Generate and save syllabus after profile update
                    user_profile_data = quiz_data

                    syllabus_content = "No syllabus generated. Please complete your profile and try again."

                    if user_profile_data:
                        profile = {
                            'level': user_profile_data.get('skill_level', 'beginner'),
                            'subject': user_profile_data.get('preferred_subjects', 'general knowledge'),
                            'style': user_profile_data.get('learning_style', 'visual'),
                            'goal': user_profile_data.get('specific_goals', 'learn new concepts')
                        }

                        prompt = f"""
Create a 2-week personalized learning plan for a {profile['level']} student.
Subject: {profile['subject']}
Learning Style: {profile['style']}
Goal: {profile['goal']}
Please structure it as a clean, detailed **HTML syllabus layout** with:
- Clear headings for weeks (`<h2>`)
- Subheadings for topics (`<h3>`)
- Bullet points for activities (`<ul>`, `<li>`)
- Sections like "Overview", "Learning Objectives", and "Resources" if relevant.
Important: Always keep the each day topics name undre <h3> tag for example <h3>Day 1-2: Topic 1</h3>. ONLY return the HTML **inside the body tag**, NOT the full HTML structure 
(no `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags). 
Just give me the **content portion** that I can embed directly into my existing Django template.
"""

                        try:
                            model = genai.GenerativeModel("gemini-2.5-flash") # Confirming model name
                            response = model.generate_content(prompt)
                            syllabus_content = response.text

                            # Save generated syllabus to Firestore
                            user_profile_ref = db.collection('user_profiles').document(firebase_uid)
                            user_profile_ref.set({'generated_syllabus': syllabus_content, 'last_updated': firestore.SERVER_TIMESTAMP}, merge=True)

                            # --- Gemini-based YouTube video recommendations ---
                            soup = BeautifulSoup(syllabus_content, 'html.parser')
                            raw_topics = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
                            topics_for_videos = []
                            for topic in raw_topics:
                                cleaned_topic = topic.lower()
                                remove_words = ['overview', 'introduction', 'basics', 'fundamentals', 'principles', 'concepts']
                                for word in remove_words:
                                    cleaned_topic = cleaned_topic.replace(word, '').strip()
                                if len(cleaned_topic) > 2 and cleaned_topic.title() not in topics_for_videos:
                                    topics_for_videos.append(cleaned_topic.title())
                            
                            recommended_videos_data = []
                            for topic in topics_for_videos:
                                channel_ids = get_relevant_channels_for_topic(topic, user_profile_data.get('preferred_subjects', ''))
                                channel_id_str = ', '.join(channel_ids) if channel_ids else 'any educational channel'
                                gemini_video_prompt = f"""
You are an expert educational video recommender. Here is the full HTML syllabus for context:
-----
{syllabus_content}
-----
For the topic: '{topic}', recommend up to 3 highly relevant YouTube videos. Only select videos from these channel IDs: {channel_id_str}.
For each video, provide:
- title
- video_id (YouTube video ID only)
- channel_title (the channel's display name)
Return the result as a JSON array like this:
[
  {{"title": "...", "video_id": "...", "channel_title": "..."}},
  ...
]
If you can't find 3, return as many as possible. Do not include videos from other channels. Only output the JSON array, nothing else.
"""
                                try:
                                    video_response = model.generate_content(gemini_video_prompt)
                                    videos = []
                                    try:
                                        videos = json.loads(video_response.text)
                                    except Exception:
                                        # Try to extract JSON from text if Gemini adds extra text
                                        import re
                                        match = re.search(r'(\[.*\])', video_response.text, re.DOTALL)
                                        if match:
                                            videos = json.loads(match.group(1))
                                    # Filter/validate structure
                                    valid_videos = [
                                        {
                                            'title': v.get('title', ''),
                                            'video_id': v.get('video_id', ''),
                                            'channel_title': v.get('channel_title', '')
                                        }
                                        for v in videos if v.get('title') and v.get('video_id')
                                    ]
                                    if valid_videos:
                                        recommended_videos_data.append({
                                            'topic': topic,
                                            'videos': valid_videos
                                        })
                                except Exception as e:
                                    print(f"Gemini video fetch error for topic '{topic}': {e}")
                                    continue
                            # Save recommended videos to Firestore
                            user_profile_ref.set({'recommended_videos': recommended_videos_data, 'last_updated': firestore.SERVER_TIMESTAMP}, merge=True)
                            # --- End Gemini-based video recommendations ---

                        except Exception as e:
                            syllabus_content = f"Error generating syllabus: {e}"
                            messages.error(request, f"Failed to generate syllabus: {e}")

                else:
                    messages.error(request, "Firebase user not found in session for profile update.")
                    return redirect('login') # Redirect to login if UID is missing
            else:
                # Handle case where user is not authenticated, perhaps redirect to login
                return redirect('login')

            # Clear quiz data from session
            if 'onboarding_quiz_data' in request.session:
                del request.session['onboarding_quiz_data']
            
            return redirect('syllabus') # Redirect to syllabus after successful generation
    else:
        form = UserProfileForm(initial=quiz_data)

    return render(request, 'onboarding_quiz.html', {'form': form})

@login_required
def dashboard_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')

    courses_progress = []
    badges = []
    quiz_results_history = []

    if firebase_uid:
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()
            badges = user_profile.get('badges', [])
            quiz_results_history = user_profile.get('quiz_results_history', [])
            quiz_results_history = sorted(
                [q for q in quiz_results_history if 'timestamp' in q],
                key=lambda x: x['timestamp'], reverse=True
            )[:7]
            quiz_results_history = list(reversed(quiz_results_history))
            
            # Get course progress from all_courses
            all_courses = user_profile.get('all_courses', [])
            for course in all_courses:
                courses_progress.append({
                    'coursename': course.get('coursename', 'Unknown Course'),  # Use the stored course name
                    'progress': course.get('progress', 0),
                    'last_activity': course.get('last_activity', 'Never'),
                    'status': course.get('status', 'Not Started')
                })

    context = {
        'user_profile': user_profile,
        'courses_progress': courses_progress,
        'badges': badges,
        'quiz_results_history': json.dumps(quiz_results_history, default=str),
    }
    return render(request, 'dashboard.html', context)

@login_required
def syllabus_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    syllabus = "No syllabus generated. Please complete your profile by taking the Onboarding Quiz."
    parsed_syllabus = []

    if firebase_uid:
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()
            # Retrieve and parse the stored syllabus
            syllabus = user_profile.get('generated_syllabus', "")

    context = {
        'user_profile': user_profile,
        'syllabus': syllabus,
    }
    return render(request, 'syllabus.html', context)

@login_required
def lesson_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    recommended_videos = []
    completed_videos = set()
    course_name = "General Knowledge"

    if firebase_uid:
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()
            recommended_videos = user_profile.get('recommended_videos', [])
            
            # Get course name from preferred subjects
            preferred_subjects = user_profile.get('specific_goals', '')
            print(f"Debug - Lesson view - Preferred subjects: {preferred_subjects}")
            if preferred_subjects and preferred_subjects.strip():
                # Handle multiple subjects (comma-separated) and extract the first one
                subjects_list = [subject.strip() for subject in preferred_subjects.split(',')]
                primary_subject = subjects_list[0].title()
                course_name = primary_subject
            else:
                course_name = "Learning Course"
            
            # Get completed videos from all courses
            all_courses = user_profile.get('all_courses', [])
            for course in all_courses:
                completed_videos.update(course.get('completed_videos', []))
    
    context = {
        'user_profile': user_profile,
        'recommended_videos': recommended_videos,
        'completed_videos': completed_videos,
        'course_name': course_name,
    }
    return render(request, 'lesson.html', context)

@login_required
def quiz_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    syllabus_content = "No syllabus found. Please complete your profile by taking the Onboarding Quiz."
    recently_asked_quizzes = [] # This will store previous quiz contents

    if firebase_uid:
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()
            syllabus_content = user_profile.get('generated_syllabus', syllabus_content)
            soup = BeautifulSoup(syllabus_content, "html.parser")
            syllabus_content = soup.get_text(separator='\n', strip=True)
            recently_asked_quizzes = user_profile.get('recently_asked_quizzes', [])
            #print(syllabus_content)
    if request.method == 'POST':
        # This branch handles both quiz preference submission and actual quiz submission
        if 'quiz_preferences_submitted' in request.POST:
            quiz_difficulty = request.POST.get('quiz_difficulty', 'beginner')
            num_questions = request.POST.get('num_questions', 5)
            question_language = request.POST.get('question_language', 'english')
            question_type = request.POST.get('question_type', 'mcq')


            preferred_subjects = user_profile.get('preferred_subjects', 'general knowledge') if user_profile else 'general knowledge'
            specific_goals = user_profile.get('specific_goals', 'learn new concepts') if user_profile else 'learn new concepts'

            try:
                num_questions = int(num_questions)
                if not (2 <= num_questions <= 10):
                    raise ValueError("Number of questions must be between 2 and 10.")
            except ValueError as e:
                messages.error(request, f"Invalid number of questions: {e}")
                return render(request, 'quiz.html', {
                    'user_profile': user_profile,
                    'show_quiz_preferences': True,
                    'error_message': f"Invalid number of questions: {e}"
                })


            # Construct prompt for Gemini API to generate quiz
            prompt = f"""
            Based on the following syllabus, user's preferred subjects: {preferred_subjects}, and specific goals: {specific_goals}, and previous quiz contents, generate a {num_questions}-question quiz with '{quiz_difficulty}' difficulty, in {question_language} language.

            Question Type: {question_type}
            {f'If the question type is MCQ, provide four options and indicate that the user should choose one. Do NOT include correct answers.' if question_type == 'mcq' else ''}
            {f'If the question type is short_answer, ensure the answer can be given in 5-10 lines. Do NOT include correct answers.' if question_type == 'short_answer' else ''}

            Syllabus:
            {syllabus_content}

            Recently asked quizzes (for context, do not repeat questions from these if possible):
            {json.dumps(recently_asked_quizzes) if recently_asked_quizzes else 'No previous quizzes.'}

            Please structure the quiz as a clean, detailed **HTML layout** 
            Question: The answer of the questions must not too big.User can answer in 5-10 lines.
            Contains mcqs,short one line answers etc accourding to subject and courses.
            with:
            - Clear heading for the quiz title (`<h2>` or `<h1>`)
            - Numbered list for questions (`<ol>`, `<li>`)
            - For each question, provide a clear label and an input field for the user to type their answers. Use `<input type="text" name="question_X_answer">` where X is the 1-indexed question number.
            - Make the answer field such that when i press enter or the line is end of the box go to new line and expand the box.
            - Important: Do NOT include correct answers or hints in the generated HTML.
            - Include a submit button for the quiz.Submit button should be like this <button type="submit" class="btn btn-primary mt-4">Submit Quiz</button>
            Important: ONLY return the HTML **inside the body tag**, NOT the full HTML structure (no `<!DOCTYPE>`, `<html>`, `<head>`,`<form>`, or `<body>` tags).
            """

            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                generated_quiz_html = response.text

                # Store the generated quiz for later verification and as "recently asked"
                if firebase_uid:
                    updated_recently_asked_quizzes = recently_asked_quizzes + [generated_quiz_html]
                    updated_recently_asked_quizzes = updated_recently_asked_quizzes[-3:]

                    db.collection('user_profiles').document(firebase_uid).set(
                        {
                            'current_quiz_html': generated_quiz_html,
                            'recently_asked_quizzes': updated_recently_asked_quizzes,
                            'last_updated': firestore.SERVER_TIMESTAMP
                        },
                        merge=True
                    )
                
                # Set a session variable to indicate that a quiz has been generated and should be displayed
                request.session['quiz_generated'] = True
                request.session['current_quiz_html'] = generated_quiz_html

                return render(request, 'quiz.html', {
                    'quiz_content': generated_quiz_html,
                    'user_profile': user_profile,
                    'show_quiz_preferences': False # Indicate not to show preferences anymore
                })

            except Exception as e:
                messages.error(request, f"Failed to generate quiz: {e}")
                request.session['quiz_generated'] = False
                # Fallback to showing preferences again or an error message
                return render(request, 'quiz.html', {
                    'user_profile': user_profile,
                    'show_quiz_preferences': True,
                    'error_message': f"Failed to generate quiz: {e}"
                })
        
        elif 'quiz_submission' in request.POST:
            # User submitted answers to the generated quiz
            user_answers = {}
            for key, value in request.POST.items():
                if key.startswith('question_') and key.endswith('_answer'):
                    question_num = key.split('_')[1]
                    user_answers[f'question_{question_num}'] = value # Store as question_1, question_2, etc.

            # Retrieve the original quiz from session or Firestore
            current_quiz_html = request.session.get('current_quiz_html')
            if not current_quiz_html and firebase_uid:
                doc = db.collection('user_profiles').document(firebase_uid).get()
                if doc.exists:
                    current_quiz_html = doc.to_dict().get('current_quiz_html')


            if current_quiz_html:
                # Prepare prompt for Gemini API to verify answers
                verification_prompt = f"""
                You are given a quiz in HTML format and a user's answers in JSON.
                Please verify the user's answers against the questions in the quiz HTML.If no answer selected mark it as incorrect.
                For each question, indicate if the user's answer is correct or incorrect. If incorrect, provide the correct answer or a detailed explanation.
                At the end, provide a summary of the user's performance, including the number of correct answers.
                
                Quiz HTML (use this to understand the questions):
                {current_quiz_html}

                User's Answers (JSON format, where keys are "question_X" and values are user's answers):
                {json.dumps(user_answers)}

                Provide the feedback in a clean, detailed HTML format. Use appropriate headings and lists.Mark the word Correct in green and incorrect in red for both bangla and english.Make divider between each question answer.
                **CRITICAL:** The output MUST ONLY be the HTML content for the body. DO NOT include `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags. ONLY the content that goes inside the `<body>`.
                At the end, also output a JSON object on a separate line with the following format:
                {{"correct": X, "incorrect": Y}}
                where X is the number of correct answers and Y is the number of incorrect answers.
                """

                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(verification_prompt)
                    verification_results_html = response.text

                    # Extract correct/incorrect count from Gemini's response
                    correct_count, incorrect_count = 0, 0
                    score_json_found = False

                    # Try regex match
                    json_match = re.search(r'\{\s*"correct"\s*:\s*(\d+),\s*"incorrect"\s*:\s*(\d+)\s*\}', verification_results_html)
                    if json_match:
                        correct_count = int(json_match.group(1))
                        incorrect_count = int(json_match.group(2))
                        # Remove the JSON line from HTML
                        verification_results_html = re.sub(r'\{\s*"correct"\s*:\s*\d+,\s*"incorrect"\s*:\s*\d+\s*\}', '', verification_results_html).strip()
                        score_json_found = True
                    else:
                        # Fallback: try parsing last line
                        lines = verification_results_html.strip().splitlines()
                        if lines:
                            last_line = lines[-1].strip()
                            try:
                                parsed_json = json.loads(last_line)
                                correct_count = parsed_json.get("correct", 0)
                                incorrect_count = parsed_json.get("incorrect", 0)
                                # Remove last line from HTML
                                verification_results_html = '\n'.join(lines[:-1]).strip()
                                score_json_found = True
                            except Exception as e:
                                print(f"[ERROR] JSON parse fallback failed: {e}")

                    # --- Clean Gemini's HTML output ---
                    soup = BeautifulSoup(verification_results_html, 'html.parser')
                    body_content = soup.find('body')
                    if body_content:
                        cleaned_results_html = ''.join(str(x) for x in body_content.contents)
                    else:
                        cleaned_results_html = verification_results_html  # Use full if <body> not found

                    # --- Save to Firestore ---
                    if score_json_found and firebase_uid:
                        db.collection('user_profiles').document(firebase_uid).set({
                            'quiz_results_history': firestore.ArrayUnion([{
                                'timestamp': datetime.utcnow(),
                                'correct': correct_count,
                                'incorrect': incorrect_count
                            }])
                        }, merge=True)

                    # Parse the generated HTML to ensure only body content is used
                    soup = BeautifulSoup(verification_results_html, 'html.parser')
                    body_content = soup.find('body')
                    if body_content:
                        # Get the inner HTML of the body tag
                        cleaned_results_html = ''.join(str(x) for x in body_content.contents)
                    else:
                        print("[WARNING] Gemini API response for quiz results did not contain a <body> tag. Using raw HTML.")
                        cleaned_results_html = verification_results_html

                    # Store results if needed, or just display
                    request.session['quiz_results_html'] = cleaned_results_html
                    request.session['quiz_generated'] = False # Reset for next quiz
                    request.session['current_quiz_html'] = None # Clear current quiz HTML

                    return render(request, 'quiz.html', {
                        'quiz_results_html': cleaned_results_html,
                        'user_profile': user_profile,
                        'show_quiz_preferences': False,
                        'show_quiz_questions': False, # Indicate not to show questions anymore
                        'show_quiz_results': True # Indicate to show results
                    })

                except Exception as e:
                    messages.error(request, f"Failed to verify quiz: {e}")
                    return render(request, 'quiz.html', {
                        'user_profile': user_profile,
                        'show_quiz_preferences': False,
                        'show_quiz_questions': True, # Keep showing questions if verification fails
                        'quiz_content': current_quiz_html,
                        'error_message': f"Failed to verify quiz: {e}"
                    })
            else:
                messages.error(request, "No quiz found to verify. Please generate a new quiz.")
                request.session['quiz_generated'] = False
                request.session['current_quiz_html'] = None
                return redirect('quiz') # Redirect to start fresh
        else:
            # Fallback for unexpected POST, maybe redirect or show error
            messages.error(request, "Invalid quiz action.")
            return redirect('quiz')

    else: # GET request
        # Initial load or after a redirect, check if a quiz was generated previously
        quiz_content = request.session.get('current_quiz_html')
        quiz_results_html = request.session.get('quiz_results_html')
        
        if quiz_results_html:
            # If results are in session, display them
            request.session['quiz_results_html'] = None # Clear after display
            return render(request, 'quiz.html', {
                'quiz_results_html': quiz_results_html,
                'user_profile': user_profile,
                'show_quiz_preferences': False,
                'show_quiz_questions': False,
                'show_quiz_results': True
            })
        elif request.session.get('quiz_generated') and quiz_content:
            # If a quiz was generated, display it
            return render(request, 'quiz.html', {
                'quiz_content': quiz_content,
                'user_profile': user_profile,
                'show_quiz_preferences': False, # Hide preferences
                'show_quiz_questions': True # Show quiz questions
            })
        else:
            # Otherwise, show quiz preferences
            return render(request, 'quiz.html', {
                'user_profile': user_profile,
                'show_quiz_preferences': True # Show preferences
            })

#!...NOTE VIEW.....
@login_required
def notes_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    notes_pdfs = {}

    if firebase_uid:
        # Get user profile data
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()
        
        # Get notes from subcollections using the new function
        notes_pdfs = get_notes_from_firestore(firebase_uid)

    context = {
        'user_profile': user_profile,
        'notes_pdfs': notes_pdfs,
    }
    return render(request, 'notes.html', context)

@login_required
def settings_feedback_view(request):
    user_profile = None
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    if firebase_uid:
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        if doc.exists:
            user_profile = doc.to_dict()

    if request.method == 'POST':
        # Handle profile image upload
        profile_image_url = user_profile.get('profile_image_url') if user_profile else None
        if 'profile_image' in request.FILES:
            image_file = request.FILES['profile_image']
            bucket = storage.bucket()
            blob = bucket.blob(f'user_avatars/{firebase_uid}/{image_file.name}')
            blob.upload_from_file(image_file, content_type=image_file.content_type)
            blob.make_public()
            profile_image_url = blob.public_url
            db.collection('user_profiles').document(firebase_uid).set({'profile_image_url': profile_image_url}, merge=True)

        # Handle username update (first_name, last_name)
        username = request.POST.get('username')
        if username:
            # Split username into first and last name if possible
            parts = username.strip().split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            db.collection('user_profiles').document(firebase_uid).set({
                'first_name': first_name,
                'last_name': last_name
            }, merge=True)

        # Handle email update
        email = request.POST.get('email-settings')
        if email and user_profile and email != user_profile.get('email'):
            try:
                user = auth.get_user(firebase_uid)
                auth.update_user(firebase_uid, email=email)
                db.collection('user_profiles').document(firebase_uid).set({'email': email}, merge=True)
            except Exception as e:
                messages.error(request, f'Failed to update email: {e}')

        # Handle password update
        password = request.POST.get('password-settings')
        if password:
            try:
                auth.update_user(firebase_uid, password=password)
            except Exception as e:
                messages.error(request, f'Failed to update password: {e}')

        messages.success(request, 'Profile updated successfully!')
        # Refresh user_profile after update
        doc = db.collection('user_profiles').document(firebase_uid).get()
        if doc.exists:
            user_profile = doc.to_dict()

    return render(request, 'settings_feedback.html', {'user_profile': user_profile})

def logout_view(request):
    if 'firebase_user' in request.session:
        del request.session['firebase_user']
    logout(request)
    return redirect('landing')

@login_required
@require_POST
def mark_video_complete(request):
    """Mark a video as complete and update course progress"""
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        video_title = data.get('video_title')
        topic = data.get('topic')
        
        if not all([video_id, video_title, topic]):
            return JsonResponse({'success': False, 'error': 'Missing required data'})
        
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        if not firebase_uid:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
        
        # Get user's course progress from Firebase
        user_ref = db.collection('user_profiles').document(firebase_uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            all_courses = user_data.get('all_courses', [])
            
            # Get course name from preferred subjects (syllabus-based)
            specific_goals = user_data.get('specific_goals', '')
            print(f"Debug - Preferred subjects: {specific_goals}")
            
            if specific_goals and specific_goals.strip():
                # Handle multiple subjects (comma-separated) and extract the first one
                subjects_list = [subject.strip() for subject in specific_goals.split(',')]
                primary_subject = subjects_list[0].title()
                course_name = primary_subject
            else:
                # Try to get course name from existing courses or use a better fallback
                if all_courses:
                    course_name = all_courses[0].get('coursename', 'Learning Course')
                else:
                    course_name = "Learning Course"
        else:
            all_courses = []
            course_name = "Learning Course"
        
        # Find or create course entry
        course_found = False
        current_course = None
        
        for course in all_courses:
            if course.get('coursename') == course_name:
                course_found = True
                current_course = course
                # Check if video is already completed
                completed_videos = course.get('completed_videos', [])
                if video_id not in completed_videos:
                    completed_videos.append(video_id)
                    course['completed_videos'] = completed_videos
                    course['last_activity'] = timezone.now().isoformat()
                    
                    # Calculate progress based on total videos in the course
                    # Get total videos from recommended_videos
                    total_videos = 0
                    recommended_videos = user_data.get('recommended_videos', [])
                    for topic_data in recommended_videos:
                        total_videos += len(topic_data.get('videos', []))
                    
                    # If no recommended videos, use default estimate
                    if total_videos == 0:
                        total_videos = 15
                    
                    progress_per_video = 100 / total_videos
                    current_progress = len(completed_videos) * progress_per_video
                    course['progress'] = min(current_progress, 100)
                    
                    # Update status based on progress
                    if course['progress'] >= 100:
                        course['status'] = 'Completed'
                    elif course['progress'] >= 1:
                        course['status'] = 'In Progress'
                    else:
                        course['status'] = 'Started'
                break
        
        # If course not found, create new course entry
        if not course_found:
            # Calculate total videos for progress calculation
            total_videos = 0
            recommended_videos = user_data.get('recommended_videos', []) if user_data else []
            for topic_data in recommended_videos:
                total_videos += len(topic_data.get('videos', []))
            
            if total_videos == 0:
                total_videos = 15
            
            progress_per_video = 100 / total_videos
            initial_progress = progress_per_video
            
            new_course = {
                'coursename': course_name,
                'progress': initial_progress,
                'last_activity': timezone.now().isoformat(),
                'status': 'Started',
                'completed_videos': [video_id]
            }
            all_courses.append(new_course)
            current_course = new_course
        
        # Update user document in Firebase
        user_ref.set({
            'all_courses': all_courses
        }, merge=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Video marked as complete',
            'progress': current_course.get('progress', progress_per_video) if current_course else progress_per_video
        })
        
    except Exception as e:
        print(f"Error marking video complete: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def generate_study_notes(request):
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    if not firebase_uid:
        return JsonResponse({'success': False, 'error': 'User not authenticated.'})

    try:
        user_ref = db.collection('user_profiles').document(firebase_uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return JsonResponse({'success': False, 'error': 'User profile not found.'})
        
        user_profile_data = user_doc.to_dict()
        syllabus_content = user_profile_data.get('generated_syllabus')
        skill_level = user_profile_data.get('skill_level', 'beginner')
        specific_goals = user_profile_data.get('specific_goals', 'learn new concepts')
        if not syllabus_content:
            return JsonResponse({'success': False, 'error': 'No syllabus found. Please complete the onboarding quiz.'})

        soup = BeautifulSoup(syllabus_content, 'html.parser')
        raw_topics = []
        # Extract topics from H2 and H3 tags within the syllabus HTML
        for heading in soup.find_all(['h3']):
            topic = heading.get_text(strip=True)
            if topic and topic not in ["Overview", "Learning Objectives", "Resources", "Week 1", "Week 2", "Week 3", "Week 4"]:# Filter out common non-topic headings
                raw_topics.append(topic)
        
        if not raw_topics:
            return JsonResponse({'success': False, 'error': 'No topics found in the syllabus to generate notes for.'})

        new_notes_generated = []
        # Determine the course name from specific_goals, taking the first one if comma-separated
        determined_course_name = "General Learning"
        if specific_goals and specific_goals.strip():
            goals_list = [goal.strip() for goal in specific_goals.split(',')]
            determined_course_name = goals_list[0].title()
        
        for topic in raw_topics:
            print(f"Generating notes for topic: {topic}")
            
            # Step 1: Generate structured content using Gemini (now includes web search internally)
            gemini_content = generate_structured_content_with_gemini(topic, skill_level, specific_goals)
            
            # Step 2: Parse Gemini content into sections
            content_sections = parse_gemini_content_to_sections(gemini_content)
            
            if content_sections.get('notes') and content_sections.get('assignment'):
                # Step 3: Generate PDF
                pdf_content_base64 = generate_pdf_from_content(content_sections, topic, firebase_uid)
                
                if pdf_content_base64:
                    # Step 4: Save PDF content to Firestore with the determined course name
                    if save_note_to_firestore(firebase_uid, topic, pdf_content_base64, determined_course_name):
                        new_notes_generated.append({'topic': topic, 'pdf_url': pdf_content_base64, 'course_name': determined_course_name})
                    else:
                        print(f"Failed to save PDF for topic: {topic}")
                else:
                    print(f"Failed to generate PDF for topic: {topic}")
            else:
                print(f"Gemini did not return complete notes and assignment for topic: {topic}")

        if new_notes_generated:
            return JsonResponse({'success': True, 'message': f'{len(new_notes_generated)} notes generated successfully!', 'notes': new_notes_generated})
        else:
            return JsonResponse({'success': False, 'error': 'No notes could be generated. Please ensure your syllabus has clear topics.'})

    except Exception as e:
        print(f"Error generating study notes: {e}")
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})


def migrate_old_notes_to_subcollections(user_id):
    """
    Migrate existing notes from the old array structure to the new subcollection structure.
    This function should be called once per user to migrate their existing data.
    """
    try:
        user_profile_ref = db.collection('user_profiles').document(user_id)
        user_doc = user_profile_ref.get()
        
        if not user_doc.exists:
            print(f"User profile not found for {user_id}")
            return False
        
        user_data = user_doc.to_dict()
        old_notes_pdfs = user_data.get('notes_pdfs', [])
        
        if not old_notes_pdfs:
            print(f"No old notes found for user {user_id}")
            return True  # No old notes to migrate
        
        print(f"Found {len(old_notes_pdfs)} course entries to migrate for user {user_id}")
        migrated_count = 0
        failed_count = 0
        
        for course_entry in old_notes_pdfs:
            course_name = course_entry.get('coursename', 'Untitled Course')
            notes_list = course_entry.get('notes', [])
            
            print(f"Migrating course: {course_name} with {len(notes_list)} notes")
            
            for note in notes_list:
                topic = note.get('topic', '')
                pdf_url = note.get('pdf_url', '')
                
                if topic and pdf_url:
                    # Save to new subcollection structure
                    if save_note_to_firestore(user_id, topic, pdf_url, course_name):
                        migrated_count += 1
                        print(f"Successfully migrated note: {topic}")
                    else:
                        failed_count += 1
                        print(f"Failed to migrate note: {topic}")
                else:
                    print(f"Skipping note with missing topic or pdf_url: {note}")
        
        # Only remove old notes_pdfs array if migration was successful
        if migrated_count > 0:
            user_profile_ref.update({
                'notes_pdfs': firestore.DELETE_FIELD
            })
            print(f"Removed old notes_pdfs array from user profile")
        
        print(f"Migration completed for user {user_id}: {migrated_count} successful, {failed_count} failed")
        return migrated_count > 0
        
    except Exception as e:
        print(f"Error migrating notes for user {user_id}: {e}")
        return False


@login_required
@require_POST
def delete_study_note(request):
    """Delete a specific study note from Firestore subcollections"""
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    if not firebase_uid:
        return JsonResponse({'success': False, 'error': 'User not authenticated.'})

    try:
        data = json.loads(request.body)
        course_name = data.get('course_name')
        topic = data.get('topic')
        
        if not course_name or not topic:
            return JsonResponse({'success': False, 'error': 'Missing course_name or topic.'})
        
        if delete_note_from_firestore(firebase_uid, course_name, topic):
            return JsonResponse({'success': True, 'message': f'Note "{topic}" deleted successfully!'})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to delete note.'})
            
    except Exception as e:
        print(f"Error deleting study note: {e}")
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})


@login_required
@require_POST
def migrate_user_notes(request):
    """Migrate user's existing notes from old structure to new subcollection structure"""
    firebase_uid = request.session.get('firebase_user', {}).get('uid')
    if not firebase_uid:
        return JsonResponse({'success': False, 'error': 'User not authenticated.'})

    try:
        if migrate_old_notes_to_subcollections(firebase_uid):
            return JsonResponse({'success': True, 'message': 'Notes migrated successfully!'})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to migrate notes.'})
            
    except Exception as e:
        print(f"Error migrating user notes: {e}")
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})
