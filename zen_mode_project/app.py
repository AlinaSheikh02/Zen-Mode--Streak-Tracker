from flask import Flask, request, jsonify, render_template
from datetime import date, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zenmode.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    current_streak = db.Column(db.Integer, default=1)
    longest_streak = db.Column(db.Integer, default=1)
    last_updated = db.Column(db.Date, nullable=False)

class StudyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    study_date = db.Column(db.Date, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_subject', methods=['POST'])
def add_subject():
    data = request.get_json()
    subject_name = data.get('subject_name')
    if Subject.query.filter_by(name=subject_name).first():
        return jsonify({'message': 'Subject already exists'})
    new_subject = Subject(name=subject_name)
    db.session.add(new_subject)
    db.session.commit()
    return jsonify({'message': 'Subject added successfully'})

@app.route('/update_streak', methods=['POST'])
def update_streak():
    data = request.get_json()
    subject_name = data.get('subject')
    today = date.today()
    
    streak = Streak.query.filter_by(subject=subject_name).first()

    if streak:
        if streak.last_updated == today:
            message = "Already updated today"
        else:
            yesterday = today - timedelta(days=1)
            if streak.last_updated == yesterday:
                streak.current_streak += 1
            else:
                streak.current_streak = 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            streak.last_updated = today
            message = "Streak updated"
    else:
        streak = Streak(subject=subject_name, current_streak=1, longest_streak=1, last_updated=today)
        db.session.add(streak)
        message = "New subject added"

    db.session.commit()
    return jsonify({'message': message})

@app.route('/log_study', methods=['POST'])
def log_study():
    data = request.get_json()
    subject = data.get('subject')
    content = data.get('content')
    today = date.today()

    log = StudyLog(subject=subject, content=content, study_date=today)
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'Study log saved'})

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    result = []
    for subject in subjects:
        streak = Streak.query.filter_by(subject=subject.name).first()
        logs = StudyLog.query.filter_by(subject=subject.name).all()
        notes = [{'text': log.content, 'date': log.study_date.isoformat()} for log in logs]
        result.append({
            'id': subject.id,
            'name': subject.name,
            'streak': streak.current_streak if streak else 0,
            'bestStreak': streak.longest_streak if streak else 0,
            'notes': notes
        })
    return jsonify(result)

@app.route('/get_stats')
def get_stats():
    total_subjects = Subject.query.count()
    total_sessions = StudyLog.query.count()
    best_streak = db.session.query(db.func.max(Streak.longest_streak)).scalar() or 0
    return jsonify({
        'total_subjects': total_subjects,
        'total_sessions': total_sessions,
        'best_streak': best_streak
    })

@app.route('/get_all_logs')
def get_all_logs():
    subjects = Subject.query.all()
    logs = StudyLog.query.all()
    subject_logs = {}
    for subject in subjects:
        subject_logs[subject.id] = {
            "name": subject.name,
            "notes": []
        }
    for log in logs:
        for subject in subjects:
            if log.subject == subject.name:
                subject_logs[subject.id]["notes"].append({
                    "note": log.content,
                    "timestamp": log.study_date.strftime("%Y-%m-%d")
                })
    return jsonify(subject_logs)

@app.route('/get_logs/<int:subject_id>')
def get_logs(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify([])
    logs = StudyLog.query.filter_by(subject=subject.name).order_by(StudyLog.study_date.desc()).all()
    return jsonify([{
        'date': log.study_date.strftime('%Y-%m-%d'),
        'note': log.content
    } for log in logs])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
