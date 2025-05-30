from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Microsoft Teams Shortcuts Data
TEAMS_SHORTCUTS = {
    "Start a video call": "Ctrl + Shift + U",
    "Start an audio call": "Ctrl + Shift + C",
    "Accept a video call": "Ctrl + Shift + A",
    "Accept an audio call": "Ctrl + Shift + S",
    "Decline a call": "Ctrl + Shift + D",
    "Start screen sharing": "Ctrl + Shift + E",
    "Toggle mute": "Ctrl + Shift + M",
    "Toggle camera": "Ctrl + Shift + O",
    "Open settings": "Ctrl + Comma",
    "Open help": "F1",
    "Search": "Ctrl + E",
    "Go to": "Ctrl + G",
    "Start new chat": "Ctrl + N",
    "Open filters": "Ctrl + Shift + F",
    "Go to previous list item": "Alt + Up arrow",
    "Go to next list item": "Alt + Down arrow",
    "Move selected team up": "Ctrl + Shift + Up arrow",
    "Move selected team down": "Ctrl + Shift + Down arrow",
    "Open more options menu": "Ctrl + Period",
    "Close": "Esc",
    "Zoom in": "Ctrl + Plus sign",
    "Zoom out": "Ctrl + Minus sign",
    "Reset zoom": "Ctrl + 0",
    "Open keyboard shortcuts": "Ctrl + Period",
    "Send message": "Ctrl + Enter"
}

# Quiz Questions
QUIZ_QUESTIONS = [
    {
        "question": "What is the keyboard shortcut to toggle mute in Microsoft Teams?",
        "options": ["Ctrl + Shift + M", "Ctrl + M", "Alt + M", "Shift + M"],
        "correct": 0
    },
    {
        "question": "How do you start a video call in Microsoft Teams?",
        "options": ["Ctrl + V", "Ctrl + Shift + V", "Ctrl + Shift + U", "Alt + V"],
        "correct": 2
    },
    {
        "question": "What shortcut is used to start screen sharing?",
        "options": ["Ctrl + S", "Ctrl + Shift + S", "Ctrl + Shift + E", "Alt + S"],
        "correct": 2
    },
    {
        "question": "How do you accept a video call in Teams?",
        "options": ["Ctrl + A", "Ctrl + Shift + A", "Alt + A", "Shift + A"],
        "correct": 1
    },
    {
        "question": "What is the shortcut to search in Microsoft Teams?",
        "options": ["Ctrl + F", "Ctrl + S", "Ctrl + E", "Alt + S"],
        "correct": 2
    },
    {
        "question": "How do you start a new chat in Teams?",
        "options": ["Ctrl + N", "Ctrl + C", "Alt + N", "Shift + N"],
        "correct": 0
    },
    {
        "question": "What shortcut toggles the camera on/off?",
        "options": ["Ctrl + O", "Ctrl + Shift + O", "Alt + O", "Shift + O"],
        "correct": 1
    },
    {
        "question": "How do you decline a call in Microsoft Teams?",
        "options": ["Ctrl + D", "Ctrl + Shift + D", "Alt + D", "Esc"],
        "correct": 1
    },
    {
        "question": "What is the shortcut to open Teams settings?",
        "options": ["Ctrl + S", "Ctrl + Comma", "Alt + S", "F2"],
        "correct": 1
    },
    {
        "question": "How do you zoom in within Teams?",
        "options": ["Ctrl + Plus sign", "Ctrl + Z", "Alt + Plus", "Shift + Plus"],
        "correct": 0
    },
    {
        "question": "What shortcut opens the help menu?",
        "options": ["Ctrl + H", "Alt + H", "F1", "Ctrl + F1"],
        "correct": 2
    },
    {
        "question": "How do you send a message in Teams chat?",
        "options": ["Enter", "Ctrl + Enter", "Shift + Enter", "Alt + Enter"],
        "correct": 1
    },
    {
        "question": "What is the shortcut to go to a specific location?",
        "options": ["Ctrl + G", "Ctrl + L", "Alt + G", "Shift + G"],
        "correct": 0
    },
    {
        "question": "How do you reset zoom to default in Teams?",
        "options": ["Ctrl + R", "Ctrl + 0", "Alt + 0", "Shift + 0"],
        "correct": 1
    },
    {
        "question": "What shortcut opens filters in Teams?",
        "options": ["Ctrl + F", "Ctrl + Shift + F", "Alt + F", "F3"],
        "correct": 1
    }
]

# In-memory storage for leaderboard and feedback
leaderboard = []
feedback_list = []

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/set_name', methods=['POST'])
def set_name():
    name = request.form.get('name', '').strip()
    if name:
        session['user_name'] = name
        session['score'] = 0
        session['question_number'] = 0
        return redirect(url_for('landing'))
    else:
        flash('Please enter your name')
        return redirect(url_for('landing'))

@app.route('/shortcuts')
def shortcuts():
    return render_template('shortcuts.html', shortcuts=TEAMS_SHORTCUTS)

@app.route('/quiz')
def quiz():
    if 'user_name' not in session:
        flash('Please enter your name first')
        return redirect(url_for('landing'))
    
    # Initialize quiz if starting fresh
    if 'quiz_questions' not in session:
        session['quiz_questions'] = random.sample(QUIZ_QUESTIONS, 10)
        session['question_number'] = 0
        session['score'] = 0
    
    # Check if quiz is complete
    if session['question_number'] >= 10:
        return redirect(url_for('results'))
    
    current_question = session['quiz_questions'][session['question_number']]
    return render_template('quiz.html', 
                         question=current_question, 
                         question_num=session['question_number'] + 1,
                         total_questions=10)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'user_name' not in session or 'quiz_questions' not in session:
        return redirect(url_for('landing'))
    
    selected_answer = int(request.form.get('answer', -1))
    current_question = session['quiz_questions'][session['question_number']]
    
    is_correct = selected_answer == current_question['correct']
    if is_correct:
        session['score'] += 1
    
    session['question_number'] += 1
    
    # Store the result for showing feedback
    session['last_answer_correct'] = is_correct
    session['correct_answer'] = current_question['options'][current_question['correct']]
    
    return render_template('answer_feedback.html',
                         is_correct=is_correct,
                         correct_answer=session['correct_answer'],
                         question_num=session['question_number'],
                         total_questions=10,
                         score=session['score'])

@app.route('/next_question')
def next_question():
    if session['question_number'] >= 10:
        return redirect(url_for('results'))
    return redirect(url_for('quiz'))

@app.route('/results')
def results():
    if 'user_name' not in session:
        return redirect(url_for('landing'))
    
    # Add to leaderboard if quiz completed
    if 'score' in session and session.get('question_number', 0) >= 10:
        leaderboard.append({
            'name': session['user_name'],
            'score': session['score'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        # Sort leaderboard by score (descending)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    score = session.get('score', 0)
    return render_template('results.html', score=score, total=10)

@app.route('/leaderboard')
def show_leaderboard():
    # Show top 10 scores
    top_scores = leaderboard[:10]
    return render_template('leaderboard.html', scores=top_scores)

@app.route('/feedback')
def feedback():
    if 'user_name' not in session:
        return redirect(url_for('landing'))
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_name' not in session:
        return redirect(url_for('landing'))
    
    feedback_text = request.form.get('feedback', '').strip()
    rating = request.form.get('rating', '')
    
    if feedback_text:
        feedback_list.append({
            'name': session['user_name'],
            'feedback': feedback_text,
            'rating': rating,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        flash('Thank you for your feedback!')
    
    return redirect(url_for('results'))

@app.route('/restart_quiz')
def restart_quiz():
    if 'user_name' in session:
        # Clear quiz-related session data but keep user name
        session.pop('quiz_questions', None)
        session.pop('question_number', None)
        session.pop('score', None)
        session.pop('last_answer_correct', None)
        session.pop('correct_answer', None)
    
    return redirect(url_for('quiz'))

if __name__ == '__main__':
    app.run(threaded=True)


# Create templates directory structure and files
"""
Create the following directory structure:

project/
├── app.py (this file)
└── templates/
    ├── base.html
    ├── landing.html
    ├── shortcuts.html
    ├── quiz.html
    ├── answer_feedback.html
    ├── results.html
    ├── leaderboard.html
    └── feedback.html

Templates are provided below:
"""