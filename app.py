from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
app.config["UPLOAD_FOLDER"] = "static/images"
db = SQLAlchemy(app)

# Database Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=True)

# Admin Authentication
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# Routes
@app.route('/') 
def index(): 
	return render_template('index.html') 

@app.route('/about') 
def about(): 
	return render_template('about.html') 

@app.route('/contact-us') 
def contact(): 
	return render_template('contact.html') 

@app.route('/curriculam') 
def curriculam(): 
	return render_template('curriculam.html') 

@app.route('/gallery') 
def gallery(): 
	return render_template('gallery.html') 

@app.route('/events')
def events():
    events = Event.query.all()
    return render_template("events.html", events=events)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('add_event'))
        else:
            flash("Invalid credentials, please try again.")
    return render_template("login.html")



# Add, Edit, and Delete Event on Single Page
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        # Add Event
        if action == 'add':
            title = request.form.get('title')
            description = request.form.get('description')
            image = request.files.get('image')

            if image:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_path)
            else:
                image_path = None

            new_event = Event(title=title, description=description, image=image.filename if image else None)
            db.session.add(new_event)
            db.session.commit()
            flash("Event added successfully!")

        # Edit Event
        elif action == 'edit':
            event_id = request.form.get('event_id')
            event = Event.query.get(event_id)
            if event:
                event.title = request.form.get('title')
                event.description = request.form.get('description')
                image = request.files.get('image')

                if image:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    image.save(image_path)
                    event.image = image.filename

                db.session.commit()
                flash("Event updated successfully!")

        # Delete Event
        elif action == 'delete':
            event_id = request.form.get('event_id')
            event = Event.query.get(event_id)
            if event:
                db.session.delete(event)
                db.session.commit()
                flash("Event deleted successfully!")

        return redirect(url_for('add_event'))

    # Fetch all events to display on the page
    events = Event.query.all()
    return render_template('add_event.html', events=events)


# Logout Admin
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
        print("Database created successfully!")
    app.run(debug=True)
