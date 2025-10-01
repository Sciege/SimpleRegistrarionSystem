from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database (file will be created as event_system.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)

    # Cascade makes sure deleting an Event also deletes its Registrations
    registrations = db.relationship(
        'Registration',
        backref='event',
        lazy=True,
        cascade="all, delete-orphan"
    )


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

# Create tables at startup
with app.app_context():
    db.create_all()

# WEB ROUTES
@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event_web():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        new_event = Event(name=name, date=date)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_event.html')

# Call events in index method
@app.route('/events/<int:event_id>/register', methods=['GET', 'POST'])
def register_student_web(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        student_name = request.form['name']
        new_registration = Registration(student_name=student_name, event_id=event.id)
        db.session.add(new_registration)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', event=event)

@app.route('/events/<int:event_id>/registrations')
def list_registrations_web(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('registrations.html', event=event, registrations=event.registrations)

# API ROUTES
@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    new_event = Event(name=data['name'], date=data['date'])
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event created', 'event': {'id': new_event.id, 'name': new_event.name, 'date': new_event.date}}), 201

@app.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/events', methods=['GET'])
def list_events():
    events = Event.query.all()
    event_list = [{'id': e.id, 'name': e.name, 'date': e.date} for e in events]
    return jsonify(event_list), 200

#Postman testing or client.py
@app.route('/api/events/<int:event_id>/register', methods=['POST'])
def register_student(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404

    student = request.json
    new_registration = Registration(student_name=student['name'], event_id=event.id)
    db.session.add(new_registration)
    db.session.commit()

    return jsonify({'message': f"Student {student['name']} registered for {event.name}"}), 200

@app.route('/api/events/<int:event_id>/registrations', methods=['GET'])
def list_registrations(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404

    registrations = [{'id': r.id, 'student_name': r.student_name} for r in event.registrations]
    return jsonify({'event': event.name, 'registrations': registrations}), 200

# Server Start
if __name__ == '__main__':
    app.run(debug=False)