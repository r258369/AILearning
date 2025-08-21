
from datetime import datetime
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
import requests
import json
import re
import base64
import markdown
from weasyprint import HTML, CSS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from firebase_config import db
from firebase_admin import firestore, auth, storage
import google.generativeai as genai
from .forms import UserProfileForm, SignupForm
import json
import http.client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse

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
1. Research and write clear, concise study notes (400-500 words, student-friendly tone, with relevant examples.) using your internal knowledge and web search capabilities to gather accurate and up-to-date information from reliable public sources (e.g., Wikipedia, OpenStax, Khan Academy, Byju's, etc.).
2. Create a 5-question assignment (mix of MCQ, Short problem solving Questions) based on the notes. For MCQs, provide 4 options (a-d). For Short problem solving Questions, ask questions that can be answered in 5-10 sentences.
Format for PDF:
📝 Study Notes
📄 Short problem solving Questions
'''
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"DEBUG: Gemini error for {topic}: {e}")
        return create_fallback_content(topic, level)

def get_existing_note_topics(user_id, course_name):
    """Get list of topics that already have notes generated"""
    try:
        sanitized_course_name = re.sub(r'[^a-zA-Z0-9_-]', '_', course_name.lower())
        course_ref = db.collection('user_profiles').document(user_id).collection('courses').document(sanitized_course_name)
        notes_ref = course_ref.collection('notes')
        notes = notes_ref.stream()
        
        existing_topics = []
        for note_doc in notes:
            note_data = note_doc.to_dict()
            if note_data.get('topic'):
                existing_topics.append(note_data['topic'])
        
        return existing_topics
    except Exception as e:
        print(f"DEBUG: Error getting existing notes: {e}")
        return []

def calculate_optimal_batch_size(topics, skill_level):
    """Calculate optimal batch size based on content complexity"""
    if not topics:  # 🚨 Guard against empty list
        return 1
    
    base_size = 1  # default
    
    # Adjust based on skill level (advanced content is more complex)
    if skill_level == 'advanced':
        base_size = 1
    elif skill_level == 'beginner':
        base_size = 1
    
    # Adjust based on topic complexity
    avg_topic_length = sum(len(topic) for topic in topics[:5]) / min(5, len(topics))
    if avg_topic_length > 50:  # Long topic names
        base_size = max(1, base_size - 1)
    
    return min(base_size, len(topics))


def generate_content_with_timeout(topic, skill_level, specific_goals):
    """Generate content with cross-platform timeout protection"""
    try:
        import threading
        import time
        
        # Cross-platform timeout implementation
        result = {'content': None, 'error': None, 'completed': False}
        
        def generate_content():
            try:
                content = generate_structured_content_with_gemini(topic, skill_level, specific_goals)
                result['content'] = content
                result['completed'] = True
            except Exception as e:
                result['error'] = str(e)
                result['completed'] = True
        
        # Start content generation in a separate thread
        thread = threading.Thread(target=generate_content)
        thread.daemon = True
        thread.start()
        
        # Wait for completion or timeout (30 seconds)
        thread.join(timeout=30)
        
        if not result['completed']:
            print(f"DEBUG: Content generation timeout for {topic}")
            # Use fallback content
            fallback_content = create_fallback_content(topic, skill_level)
            sections = parse_gemini_content_to_sections(fallback_content)
            return {'success': True, 'content': sections}
        
        if result['error']:
            print(f"DEBUG: Content generation error for {topic}: {result['error']}")
            # Use fallback content
            fallback_content = create_fallback_content(topic, skill_level)
            sections = parse_gemini_content_to_sections(fallback_content)
            return {'success': True, 'content': sections}
        
        if result['content']:
            sections = parse_gemini_content_to_sections(result['content'])
            if sections.get('notes') and sections.get('assignment'):
                return {'success': True, 'content': sections}
        
        # If we get here, content generation failed
        print(f"DEBUG: Incomplete content generated for {topic}")
        fallback_content = create_fallback_content(topic, skill_level)
        sections = parse_gemini_content_to_sections(fallback_content)
        return {'success': True, 'content': sections}
            
    except Exception as e:
        print(f"DEBUG: Content generation wrapper error for {topic}: {e}")
        # Always return fallback content to ensure progress
        fallback_content = create_fallback_content(topic, skill_level)
        sections = parse_gemini_content_to_sections(fallback_content)
        return {'success': True, 'content': sections}

def generate_pdf_with_optimization(content_sections, topic, user_id):
    """Generate PDF with memory optimization and fallback"""
    try:
        # First attempt with full content
        pdf_content = generate_pdf_from_content(content_sections, topic, user_id)
        if pdf_content:
            return {'success': True, 'pdf_content': pdf_content}
        
        # Fallback: Try with simplified content
        simplified_sections = {
            'notes': content_sections['notes'][:2000],  # Limit to 2000 chars
            'assignment': content_sections['assignment'][:1000]  # Limit to 1000 chars
        }
        
        pdf_content = generate_pdf_from_content(simplified_sections, topic, user_id)
        if pdf_content:
            return {'success': True, 'pdf_content': pdf_content}
        
        return {'success': False, 'error': 'PDF generation failed'}
        
    except Exception as e:
        print(f"DEBUG: PDF optimization error for {topic}: {e}")
        return {'success': False, 'error': str(e)}

def create_fallback_content(topic, level):
    """Create basic fallback content when Gemini fails"""
    return f"""
📝 Study Notes
{topic} - {level.title()} Level

This is a basic study guide for {topic}. The topic covers fundamental concepts that are important for understanding the subject matter.

Key points to remember:
- Understand the basic definitions and concepts
- Practice with examples and exercises  
- Review regularly to reinforce learning
- Connect concepts to real-world applications

📄 Assignment Questions

1. Multiple Choice: What is the main concept covered in {topic}?
   a) Basic principles
   b) Advanced theories  
   c) Practical applications
   d) All of the above

2. Fill in the blank: {topic} is important because ____________.

3. Short Answer: Explain one key concept from {topic} in your own words.
"""

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
    """Generate PDF with production-optimized memory management"""
    try:
        print(f"DEBUG: Starting PDF generation for topic: {topic}")
        
        # Convert content to HTML with memory optimization
        html_string = convert_text_to_html_for_pdf(
            topic,
            content_dict["notes"],
            content_dict["assignment"]
        )
        
        # Limit HTML content size to prevent memory issues
        max_html_size = 50000  # 50KB limit
        if len(html_string) > max_html_size:
            print(f"DEBUG: HTML content too large ({len(html_string)} chars), truncating")
            html_string = html_string[:max_html_size] + "</body></html>"

        # Generate PDF using WeasyPrint with memory constraints
        try:
            pdf_bytes = HTML(string=html_string).write_pdf()
            print(f"DEBUG: PDF generated successfully, size: {len(pdf_bytes)} bytes")
            
            # Limit PDF size to prevent Firebase/memory issues
            max_pdf_size = 1024 * 1024  # 1MB limit
            if len(pdf_bytes) > max_pdf_size:
                print(f"DEBUG: PDF too large ({len(pdf_bytes)} bytes), rejecting")
                return None
            
            # Encode to base64
            pdf_content_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Clean up memory
            del pdf_bytes
            del html_string
            
            return f"data:application/pdf;base64,{pdf_content_base64}"
            
        except Exception as weasy_error:
            print(f"DEBUG: WeasyPrint error: {weasy_error}")
            # Fallback: create simple text-based PDF content
            return create_simple_text_pdf(content_dict, topic)

    except Exception as e:
        print(f"DEBUG: PDF generation error for {topic}: {e}")
        return None

def create_simple_text_pdf(content_dict, topic):
    """Fallback: Create simple text-based content when PDF generation fails"""
    try:
        # Create simple HTML without complex styling
        simple_html = f"""
        <html>
        <head><title>{topic} - Study Notes</title></head>
        <body style="font-family: Arial; margin: 20px; line-height: 1.6;">
            <h1>{topic}</h1>
            <h2>Study Notes</h2>
            <div>{content_dict.get('notes', 'No notes available')}</div>
            <h2>Assignment</h2>
            <div>{content_dict.get('assignment', 'No assignment available')}</div>
        </body>
        </html>
        """
        
        pdf_bytes = HTML(string=simple_html).write_pdf()
        pdf_content_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Clean up
        del pdf_bytes
        del simple_html
        
        return f"data:application/pdf;base64,{pdf_content_base64}"
        
    except Exception as e:
        print(f"DEBUG: Simple PDF generation also failed: {e}")
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


#!........Login View..........
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
                    'suggested_video_titles': [],
                    'last_updated': firestore.SERVER_TIMESTAMP
                })

               
                return redirect('login') 

            except Exception as e:

                form.add_error(None, str(e))
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})



@csrf_exempt
def onboarding_quiz_view(request):
    """Simplified onboarding quiz view with better error handling"""
    quiz_data = request.session.get('onboarding_quiz_data', {})

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            print(f"DEBUG: Processing {'AJAX' if is_ajax else 'regular'} request")
            
            # Validate form
            form = UserProfileForm(request.POST, initial=quiz_data)
            if not form.is_valid():
                print(f"DEBUG: Form validation failed: {form.errors}")
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please fill in all required fields correctly.',
                        'form_errors': form.errors
                    })
                return render(request, 'onboarding_quiz.html', {'form': form, 'form_errors': form.errors})
            
            # Update quiz data
            for key, value in form.cleaned_data.items():
                quiz_data[key] = value
            request.session['onboarding_quiz_data'] = quiz_data
            
            # Check authentication
            if not request.user.is_authenticated:
                error_msg = 'User not authenticated. Please log in.'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                return redirect('login')
            
            firebase_uid = request.session.get('firebase_user', {}).get('uid')
            if not firebase_uid:
                error_msg = "Firebase user not found in session."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('login')
            
            # Save profile to Firebase and generate syllabus
            try:
                print(f"DEBUG: Saving profile to Firebase for user: {firebase_uid}")
                doc_ref = db.collection('user_profiles').document(firebase_uid)
                
                # First save the basic profile
                profile_data = {
                    'learning_style': quiz_data.get('learning_style'),
                    'preferred_subjects': quiz_data.get('preferred_subjects'),
                    'skill_level': quiz_data.get('skill_level'),
                    'specific_goals': quiz_data.get('specific_goals'),
                    'last_updated': firestore.SERVER_TIMESTAMP
                }
                doc_ref.set(profile_data, merge=True)
                print(f"DEBUG: Profile saved successfully")
                
                # Generate syllabus and videos with Gemini API
                try:
                    print(f"DEBUG: Starting syllabus generation")
                    
                    # Create profile for Gemini prompt
                    profile = {
                        'level': quiz_data.get('skill_level', 'beginner'),
                        'subject': quiz_data.get('preferred_subjects', 'general knowledge'),
                        'style': quiz_data.get('learning_style', 'visual'),
                        'goal': quiz_data.get('specific_goals', 'learn new concepts')
                    }

                    # Main syllabus prompt
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
- Make the section visually appealing with appropriate HTML tags.
Important: For each day, create an <h3> heading that includes the day number(s), the main subject, and the specific topic. Do not replace the subject with a generic topic—always mention main focus from {profile['goal']} as main subject.
Format: <h3>Day X-Y: [Main Subject] – [Specific Topic]</h3>
Example:
<h3>Day 1-2: Java Swing – Buttons and Labels</h3>
<h3>Day 3: Java Swing – Event Handling</h3> 
ONLY return the HTML **so that I just copy in my Django template**, NOT the full HTML structure 
(no `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags). 
Just give me the **content portion** that I can embed directly into my existing Django template.
"""

                    # Generate syllabus with Gemini
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    syllabus_content = response.text
                    print(f"DEBUG: Syllabus generated successfully")
                    print(f"DEBUG: Syllabus content length: {len(syllabus_content)} characters")

                    # Save the generated syllabus to Firestore
                    doc_ref.update({
                        'generated_syllabus': syllabus_content,
                        'last_updated': firestore.SERVER_TIMESTAMP
                    })
                    print(f"DEBUG: Generated syllabus saved to Firebase")

                    # Generate suggested video titles for each topic as list
                    print(f"DEBUG: Starting video title generation")

                except Exception as syllabus_error:
                    print(f"DEBUG: Syllabus generation failed: {syllabus_error}")
                    # Save a basic syllabus as fallback (only if Gemini failed)
                    print(f"DEBUG: Saving fallback syllabus due to Gemini error")
                    basic_syllabus = f"""
                    <h2>Welcome to your learning journey!</h2>
                    <p>Your profile has been saved successfully.</p>
                    <h3>Your Learning Preferences:</h3>
                    <ul>
                        <li><strong>Learning Style:</strong> {quiz_data.get('learning_style', 'Not specified')}</li>
                        <li><strong>Preferred Subjects:</strong> {quiz_data.get('preferred_subjects', 'Not specified')}</li>
                        <li><strong>Skill Level:</strong> {quiz_data.get('skill_level', 'Not specified')}</li>
                        <li><strong>Goals:</strong> {quiz_data.get('specific_goals', 'Not specified')}</li>
                    </ul>
                    <p>We'll generate your personalized syllabus and video recommendations shortly.</p>
                    """
                    
                    doc_ref.update({
                        'generated_syllabus': basic_syllabus,
                        'last_updated': firestore.SERVER_TIMESTAMP
                    })
                
            except Exception as firebase_error:
                print(f"DEBUG: Firebase error: {firebase_error}")
                error_msg = f"Failed to save profile: {str(firebase_error)}"
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return render(request, 'onboarding_quiz.html', {'form': form, 'error': error_msg})
            
            # Clear session data
            if 'onboarding_quiz_data' in request.session:
                del request.session['onboarding_quiz_data']
            
            # Return success response
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully!',
                    'redirect_url': reverse('syllabus')
                })
            else:
                return redirect('syllabus')
                
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = f'An unexpected error occurred: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            
            messages.error(request, error_msg)
            return render(request, 'onboarding_quiz.html', {'form': UserProfileForm(), 'error': error_msg})
    
    # GET request
    form = UserProfileForm(initial=quiz_data)
    return render(request, 'onboarding_quiz.html', {'form': form})




from pytube import Search
#!......Generate Videos........
@login_required
@require_POST

def generate_videos_view(request):
    try:
        user_profile = None
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        doc_ref = db.collection('user_profiles').document(firebase_uid)
        doc = doc_ref.get()
        user_profile = doc.to_dict()
        syllabus_content = user_profile.get('generated_syllabus', [])        
        print(f"DEBUG: Syllabus content length: {len(syllabus_content)} characters")
        video_prompt = f"""
Based on the following syllabus, suggest **2 YouTube video titles per topic/day** that a student should watch.Video length should be under 5-20 min. The titles should be realistic and engaging, like actual YouTube videos.
Return the result strictly as a **flat list of strings**, ignoring JSON formatting.

Syllabus:
{syllabus_content}

Example output (as list of strings):
[
"Java Swing Tutorial: Buttons and Labels Made Easy",
"Learn Java Swing Buttons & Labels in 15 Minutes",
"Java Swing Event Handling Explained with Examples",
"Mastering Event Handling in Java Swing"
]
"""
        model = genai.GenerativeModel("gemini-2.5-flash")
        video_response = model.generate_content(video_prompt)
        # Convert to Python list safely
        try:
            suggested_videos_list = eval(video_response.text.strip())
            if not isinstance(suggested_videos_list, list):
                suggested_videos_list = []
        except Exception:
            suggested_videos_list = []

        print(f"DEBUG: Video titles generated successfully: {len(suggested_videos_list)} titles")

        # Save suggested video titles as list to Firestore
        doc_ref.update({
            'suggested_video_titles': suggested_videos_list,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
        print(f"DEBUG: Suggested video titles saved to Firebase as list")
        # Check authentication first
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        if not firebase_uid:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
        
        # Get user profile and suggested video titles from Firebase
        try:
            doc_ref = db.collection('user_profiles').document(firebase_uid)
            user_doc = doc_ref.get()
            
            if not user_doc.exists:
                return JsonResponse({'success': False, 'error': 'User profile not found'})
            
            user_data = user_doc.to_dict()
            suggested_video_titles = user_data.get('suggested_video_titles', [])
            preferred_subjects = user_data.get('preferred_subjects', '')
            
        except Exception as firebase_error:
            print(f"DEBUG: Firebase error: {firebase_error}")
            return JsonResponse({'success': False, 'error': 'Failed to access user data. Please try again.'})
        
        if not suggested_video_titles:
            return JsonResponse({'success': False, 'error': 'No suggested video titles found. Please complete the onboarding quiz first.'})
        
        print(f"DEBUG: Found {len(suggested_video_titles)} suggested video titles, starting video fetch")

        recommended_videos_data = []

        # Generate videos for each suggested title (limit to avoid timeout)
        max_titles = min(10, len(suggested_video_titles))  # fetch top 10 titles to avoid long processing
        for i, title in enumerate(suggested_video_titles[:max_titles]):
            try:
                print(f"DEBUG: Fetching videos for title {i+1}/{max_titles}: {title}")

                # Optional: refine search with preferred subjects
                search_query = title
                if preferred_subjects:
                    search_query += f" {preferred_subjects}"

                # Use pytube to search
                search_results = Search(search_query).results[:1]  # get top 2 videos
                videos = []
                for video in search_results:
                    videos.append({
                        'title': video.title,
                        'video_id': video.video_id,
                        'channel_title': video.author
                    })

                # Validate structure
                valid_videos = []
                for v in videos:
                    if isinstance(v, dict) and v.get('title') and v.get('video_id'):
                        valid_videos.append({
                            'title': str(v.get('title', '')),
                            'video_id': str(v.get('video_id', '')),
                            'channel_title': str(v.get('channel_title', ''))
                        })

                if valid_videos:
                    recommended_videos_data.append({
                        'suggested_title': title,
                        'videos': valid_videos
                    })
                    print(f"DEBUG: Added {len(valid_videos)} videos for suggested title: {title}")

            except Exception as video_error:
                print(f"DEBUG: Video fetch error for suggested title: {video_error}")
                continue
        
        # Save recommended videos to Firestore
        if recommended_videos_data:
            try:
                doc_ref.update({
                    'recommended_videos': recommended_videos_data,
                    'last_updated': firestore.SERVER_TIMESTAMP
                })
                print(f"DEBUG: Saved {len(recommended_videos_data)} recommended video entries to Firebase")

                total_videos = sum(len(entry.get('videos', [])) for entry in recommended_videos_data)
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully fetched {total_videos} videos for {len(recommended_videos_data)} suggested titles!',
                    'video_count': total_videos,
                    'title_count': len(recommended_videos_data)
                })
            except Exception as save_error:
                print(f"DEBUG: Firebase save error: {save_error}")
                return JsonResponse({'success': False, 'error': 'Videos fetched but failed to save. Please try again.'})
        else:
            return JsonResponse({'success': False, 'error': 'No videos could be fetched. Please try again later.'})

    except Exception as e:
        print(f"DEBUG: Unexpected video generation error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred. Please try again later.'})








#!......dashboard view............
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


#!......syllabus view............
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


#!......lesson view............
@login_required
def lesson_view(request):
    try:
        user_profile = None
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        recommended_videos = []
        completed_videos = set()
        course_name = "General Knowledge"

        if firebase_uid:
            try:
                doc_ref = db.collection('user_profiles').document(firebase_uid)
                doc = doc_ref.get()
                
                if doc.exists:
                    user_profile = doc.to_dict()
                    recommended_videos = user_profile.get('recommended_videos', [])
                    print(f"DEBUG: Found {len(recommended_videos)} video topics")
                    
                    # Get course name from preferred subjects
                    preferred_subjects = user_profile.get('specific_goals', '') 
                    print(f"DEBUG: Preferred subjects: {preferred_subjects}")
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
                    
                    print(f"DEBUG: Course name: {course_name}")
                    print(f"DEBUG: Completed videos: {len(completed_videos)}")
                    
            except Exception as firebase_error:
                print(f"DEBUG: Firebase error in lesson view: {firebase_error}")
                # Continue with default values
        
        context = {
            'user_profile': user_profile,
            'recommended_videos': recommended_videos,
            'completed_videos': completed_videos,
            'course_name': course_name,
        }
        
        
        # Test if it's a template issue
        try:
            return render(request, 'lesson.html', context)
        except Exception as template_error:
            print(f"DEBUG: Template rendering error: {template_error}")
            # Return simple HTML for debugging
            simple_html = f"""
            <html>
            <head><title>Lesson Debug</title></head>
            <body>
                <h1>Lesson Page Debug</h1>
                <p>Course: {course_name}</p>
                <p>Videos: {len(recommended_videos)} topics</p>
                <p>User Profile: {'Found' if user_profile else 'Not found'}</p>
                <p>Template Error: {str(template_error)}</p>
            </body>
            </html>
            """
            return HttpResponse(simple_html)
        
    except Exception as e:
        print(f"DEBUG: Lesson view error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a simple error response
        
        return HttpResponse(f"Lesson view error: {str(e)}", status=500)

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
            {f'If the question type is MCQ, provide four options with radio button and indicate that the user should choose one. Do NOT include correct answers.Make questions like problem solving question' if question_type == 'mcq' else ''}
            {f'If the question type is short_answer, ensure the answer can be given in 5-10 lines. Do NOT include correct answers.Make questions like problem solving question' if question_type == 'short_answer' else ''}

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
            - For each question, provide a clear label and an input field for the user to type their answers. Use `<input type="text" name="question_X_answer">` where X is the 1-indexed question number.Dont mention anything in the input field.Maintain the input field width.
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

#!......NOTE VIEW........
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


#!.......Settings and Feedback view........
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


#!.......Logout view........
def logout_view(request):
    if 'firebase_user' in request.session:
        del request.session['firebase_user']
    logout(request)
    return redirect('landing')



#!.......Mark a video as complete........
@login_required
@require_POST
def mark_video_complete(request):
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        video_title = data.get('video_title')
        
        if not all([video_id, video_title]):
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
                    total_videos = 0
                    recommended_videos = user_data.get('recommended_videos', [])
                    for video_data in recommended_videos:
                        total_videos += len(video_data.get('videos', []))
                    
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
            for video_data in recommended_videos:
                total_videos += len(video_data.get('videos', []))
            
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
def clear_user_cache(request):
    """Clear all cached data for the user"""
    try:
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        if not firebase_uid:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
        
        # Clear session cache
        cache_keys_to_clear = [key for key in request.session.keys() if firebase_uid in key]
        for key in cache_keys_to_clear:
            del request.session[key]
        
        print(f"DEBUG: Cleared {len(cache_keys_to_clear)} cache entries for user {firebase_uid}")
        
        return JsonResponse({
            'success': True,
            'message': f'Cleared {len(cache_keys_to_clear)} cache entries. Please try generating notes again.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


#!......Generate study notes............
@login_required
@require_POST  
def generate_study_notes(request):
    """Generate study notes with advanced timeout and resource management"""
    try:
        firebase_uid = request.session.get('firebase_user', {}).get('uid')
        if not firebase_uid:
            return JsonResponse({'success': False, 'error': 'User not authenticated.'})

        print(f"DEBUG: Starting optimized note generation for user: {firebase_uid}")

        # Check if there's an ongoing generation process
        batch_mode = request.POST.get('batch_mode', 'false') == 'true'
        start_index = int(request.POST.get('start_index', 0))
        
        # Get user profile
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

        
        
        # Always extract topics from current syllabus (don't use cache to avoid stale data)
        soup = BeautifulSoup(syllabus_content, 'html.parser')
        raw_topics = []
        for heading in soup.find_all(['h3']):
            topic = heading.get_text(strip=True)
            if topic and topic not in ["Overview", "Learning Objectives", "Resources", "Week 1", "Week 2", "Week 3", "Week 4"]:
                raw_topics.append(topic)
        
        # Clear any old cached topics to prevent confusion
        cache_key = f"topics_{firebase_uid}"
        if cache_key in request.session:
            del request.session[cache_key]
        
        if not raw_topics:
            return JsonResponse({'success': False, 'error': 'No topics found in the syllabus.'})

        # Determine course name
        determined_course_name = "General Learning"
        if specific_goals and specific_goals.strip():
            goals_list = [goal.strip() for goal in specific_goals.split(',')]
            determined_course_name = goals_list[0].title()

        # Check existing notes to avoid duplicates
        existing_notes = get_existing_note_topics(firebase_uid, determined_course_name)
        remaining_topics = [topic for topic in raw_topics if topic not in existing_notes]
        
        print(f"DEBUG: Total topics: {len(raw_topics)}, Existing: {len(existing_notes)}, Remaining: {len(remaining_topics)}")

        if not remaining_topics:
            return JsonResponse({
                'success': True, 
                'message': 'All notes have already been generated!',
                'total_generated': len(existing_notes),
                'remaining_topics': 0
            })

        # Intelligent batch sizing based on content complexity
        topics_to_process = remaining_topics[start_index:]
        batch_size = calculate_optimal_batch_size(topics_to_process, skill_level)
        current_batch = topics_to_process[:batch_size]
        

        new_notes_generated = []
        
        # Process current batch with optimized resource management
        for i, topic in enumerate(current_batch):
            try:
                print(f"DEBUG: Processing topic {start_index + i + 1}/{len(raw_topics)}: {topic}")
                
                # Generate content with timeout protection
                content_result = generate_content_with_timeout(topic, skill_level, specific_goals)
                if not content_result['success']:
                    print(f"DEBUG: Content generation failed for {topic}: {content_result['error']}")
                    continue
                
                # Generate PDF with memory optimization
                pdf_result = generate_pdf_with_optimization(content_result['content'], topic, firebase_uid)
                if not pdf_result['success']:
                    print(f"DEBUG: PDF generation failed for {topic}: {pdf_result['error']}")
                    continue
                
                # Save to Firestore
                if save_note_to_firestore(firebase_uid, topic, pdf_result['pdf_content'], determined_course_name):
                    new_notes_generated.append({
                        'topic': topic, 
                        'pdf_url': pdf_result['pdf_content'], 
                        'course_name': determined_course_name
                    })
                    print(f"DEBUG: Successfully generated note for: {topic}")
                
                # Memory cleanup after each note
                import gc
                gc.collect()
                
            except Exception as topic_error:
                print(f"DEBUG: Error processing topic '{topic}': {topic_error}")
                continue

        # Calculate progress
        total_processed = start_index + len(current_batch)
        remaining_count = len(remaining_topics) - len(current_batch)
        
        # Prepare response
        if new_notes_generated:
            if remaining_count > 0:
                message = f'Generated {len(new_notes_generated)} notes successfully! {remaining_count} topics remaining.'
                # Auto-continue for next batch
                next_batch_info = {
                    'has_more': True,
                    'next_start_index': total_processed,
                    'remaining_count': remaining_count,
                    'auto_continue': True
                }
            else:
                message = f'All {len(new_notes_generated)} notes generated successfully!'
                next_batch_info = {'has_more': False}
            
            return JsonResponse({
                'success': True, 
                'message': message, 
                'notes': new_notes_generated,
                'total_generated': len(new_notes_generated),
                'progress': {
                    'current': total_processed,
                    'total': len(raw_topics),
                    'percentage': int((total_processed / len(raw_topics)) * 100)
                },
                **next_batch_info
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'No notes could be generated in this batch. Please try again.'
            })

    except Exception as e:
        print(f"DEBUG: Unexpected note generation error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': 'An unexpected error occurred. Please try again.'
        })


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
    
#!...............CHAT VIEW..........
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    genai.configure(api_key="AIzaSyBXQvI2hY5j0bir7LhZP6-fjH_DABSViys")
    try:
        # Parse incoming JSON
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Call Gemini API
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(user_message)

        # Extract response text
        content = response.text if hasattr(response, "text") else str(response)
        print(f"Gemini response: {content}")  # Debugging output
        return JsonResponse({'success': True, 'response': content})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)
@login_required
@require_POST  
def test_gemini_connection(request):
    """Test Gemini API connection"""
    try:
        print("DEBUG: Testing Gemini API connection...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello, this is a test. Please respond with 'Gemini API is working!'")
        return JsonResponse({
            'success': True,
            'message': 'Gemini API test successful',
            'response': response.text
        })
    except Exception as e:
        print(f"DEBUG: Gemini API test failed: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Gemini API test failed: {str(e)}'
        })
