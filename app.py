import os
import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
CORS(app)

# Import services
from services.auth_service import AuthService
from services.recommendation_service import RecommendationService
from services.location_service import LocationService
from services.message_service import MessageService
from services.rating_service import RatingService

# In-memory data stores
users = {}  # userId -> user object
jobs = {}   # jobId -> job object
skills = {}  # skillId -> skill object
messages = {}  # messageId -> message object
ratings = {}  # ratingId -> rating object

# Add default Indian jobs and skills
def add_sample_data():
    # Add some skills
    sample_skills = [
        {"id": "s1", "name": "Carpentry", "category": "Construction"},
        {"id": "s2", "name": "Plumbing", "category": "Home Services"},
        {"id": "s3", "name": "Electrical Work", "category": "Home Services"},
        {"id": "s4", "name": "Painting", "category": "Construction"},
        {"id": "s5", "name": "Masonry", "category": "Construction"},
        {"id": "s6", "name": "Cooking", "category": "Hospitality"},
        {"id": "s7", "name": "Driving", "category": "Transportation"},
        {"id": "s8", "name": "Gardening", "category": "Agriculture"},
        {"id": "s9", "name": "Cleaning", "category": "Home Services"},
        {"id": "s10", "name": "Tailoring", "category": "Textile"},
        {"id": "s11", "name": "Welding", "category": "Manufacturing"},
        {"id": "s12", "name": "Security", "category": "Protection Services"},
        {"id": "s13", "name": "Farm Work", "category": "Agriculture"},
        {"id": "s14", "name": "Data Entry", "category": "Office Work"},
        {"id": "s15", "name": "Retail Sales", "category": "Sales"}
    ]
    
    for skill in sample_skills:
        skills[skill["id"]] = skill
    
    # Add sample employers
    employer1 = {
        "id": "e1",
        "name": "Tata Construction Ltd",
        "email": "hiring@tataconstruction.com",
        "password": generate_password_hash("password123"),
        "user_type": "employer",
        "location": "Mumbai, Maharashtra",
        "company_size": "Large Enterprise",
        "industry": "Construction"
    }
    
    employer2 = {
        "id": "e2",
        "name": "Infosys Campus Services",
        "email": "facilities@infosys.com",
        "password": generate_password_hash("password123"),
        "user_type": "employer",
        "location": "Bangalore, Karnataka",
        "company_size": "Large Enterprise",
        "industry": "Technology"
    }
    
    employer3 = {
        "id": "e3",
        "name": "Sai Hospitality Services",
        "email": "jobs@saihospitality.com",
        "password": generate_password_hash("password123"),
        "user_type": "employer",
        "location": "Hyderabad, Telangana",
        "company_size": "Medium Business",
        "industry": "Hospitality"
    }
    
    employer4 = {
        "id": "e4",
        "name": "Godrej Properties",
        "email": "careers@godrejproperties.com",
        "password": generate_password_hash("password123"),
        "user_type": "employer",
        "location": "Delhi, NCR",
        "company_size": "Large Enterprise",
        "industry": "Real Estate"
    }
    
    employer5 = {
        "id": "e5",
        "name": "Local Farms Cooperative",
        "email": "work@localfarms.org",
        "password": generate_password_hash("password123"),
        "user_type": "employer",
        "location": "Pune, Maharashtra",
        "company_size": "Small Business",
        "industry": "Agriculture"
    }
    
    users[employer1["id"]] = employer1
    users[employer2["id"]] = employer2
    users[employer3["id"]] = employer3
    users[employer4["id"]] = employer4
    users[employer5["id"]] = employer5
    
    # Add sample jobs
    job1 = {
        "id": "j1",
        "title": "Construction Workers Needed for Township Project",
        "description": "We are looking for experienced construction workers for our upcoming township project in Mumbai suburbs. Skills required include masonry, carpentry, and painting. Daily wages provided with meals. 3-month contract with possibility of extension.",
        "location": "Thane, Maharashtra",
        "skills_required": ["Carpentry", "Masonry", "Painting"],
        "pay_rate": "600",
        "duration": "3 months",
        "employer_id": "e1",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
        "applications": []
    }
    
    job2 = {
        "id": "j2",
        "title": "Campus Maintenance Staff",
        "description": "Infosys Bangalore campus is hiring maintenance staff for electrical work, plumbing, and gardening. Full-time positions with benefits including health insurance, PF, and on-campus accommodation.",
        "location": "Electronic City, Bangalore",
        "skills_required": ["Electrical Work", "Plumbing", "Gardening"],
        "pay_rate": "22000",
        "duration": "Permanent",
        "employer_id": "e2",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat(),
        "applications": []
    }
    
    job3 = {
        "id": "j3",
        "title": "Hotel Kitchen Assistants and Cleaners",
        "description": "5-star hotel in Hyderabad looking for kitchen assistants and cleaning staff. Experience preferred but not required. Shift work with overtime pay. Meals provided during shifts.",
        "location": "Banjara Hills, Hyderabad",
        "skills_required": ["Cooking", "Cleaning"],
        "pay_rate": "15000",
        "duration": "Permanent",
        "employer_id": "e3",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
        "applications": []
    }
    
    job4 = {
        "id": "j4",
        "title": "Drivers for Corporate Fleet",
        "description": "Godrej is hiring experienced drivers for corporate fleet in Delhi NCR. Must have valid commercial license and 3+ years experience. Company transport provided to/from home.",
        "location": "Gurgaon, Haryana",
        "skills_required": ["Driving"],
        "pay_rate": "18000",
        "duration": "Permanent",
        "employer_id": "e4",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(),
        "applications": []
    }
    
    job5 = {
        "id": "j5",
        "title": "Seasonal Farm Workers",
        "description": "Local Farms Cooperative needs farm workers for the upcoming harvest season. Work includes vegetable picking, sorting, and packaging. Transportation provided from Pune city center.",
        "location": "Mulshi, Pune",
        "skills_required": ["Farm Work", "Gardening"],
        "pay_rate": "450",
        "duration": "45 days",
        "employer_id": "e5",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
        "applications": []
    }
    
    job6 = {
        "id": "j6",
        "title": "Security Guards for Residential Complex",
        "description": "Tata Housing needs security personnel for our residential complexes in Mumbai. 8-hour shifts (rotating). Previous security experience preferred.",
        "location": "Vikhroli, Mumbai",
        "skills_required": ["Security"],
        "pay_rate": "16000",
        "duration": "Permanent",
        "employer_id": "e1",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=8)).isoformat(),
        "applications": []
    }
    
    job7 = {
        "id": "j7",
        "title": "Office Assistants for Data Entry",
        "description": "Infosys BPO division requires data entry operators with basic computer knowledge. Day shift only. Training provided.",
        "location": "Whitefield, Bangalore",
        "skills_required": ["Data Entry"],
        "pay_rate": "16500",
        "duration": "6 months",
        "employer_id": "e2",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=4)).isoformat(),
        "applications": []
    }
    
    job8 = {
        "id": "j8",
        "title": "Tailors for Uniform Stitching",
        "description": "Hotel chain looking for experienced tailors to stitch and repair staff uniforms. Must have experience with industrial sewing machines.",
        "location": "Secunderabad, Telangana",
        "skills_required": ["Tailoring"],
        "pay_rate": "18000",
        "duration": "Permanent",
        "employer_id": "e3",
        "status": "open",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=15)).isoformat(),
        "applications": []
    }
    
    jobs[job1["id"]] = job1
    jobs[job2["id"]] = job2
    jobs[job3["id"]] = job3
    jobs[job4["id"]] = job4
    jobs[job5["id"]] = job5
    jobs[job6["id"]] = job6
    jobs[job7["id"]] = job7
    jobs[job8["id"]] = job8

# Initialize services
auth_service = AuthService(users)
recommendation_service = RecommendationService(users, jobs, skills)
location_service = LocationService(users, jobs)
message_service = MessageService(users, messages)
rating_service = RatingService(users, ratings, jobs)

# Add sample data
add_sample_data()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = auth_service.authenticate(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if auth_service.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        user = auth_service.register_user(name, email, password, user_type)
        if user:
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        session.clear()
        flash('User not found', 'danger')
        return redirect(url_for('login'))
    
    user_type = user['user_type']
    
    if user_type == 'worker':
        # For workers, show recommended jobs
        recommended_jobs = recommendation_service.get_recommended_jobs(user_id)
        
        # Get a list of worker's job applications
        worker_applications = []
        for job_id, job in jobs.items():
            for application in job.get('applications', []):
                if application.get('worker_id') == user_id:
                    # Add job details to the application
                    app_with_details = dict(application)
                    app_with_details['job_id'] = job_id
                    app_with_details['job_title'] = job.get('title')
                    app_with_details['employer_id'] = job.get('employer_id')
                    
                    # Get employer name
                    employer = auth_service.get_user_by_id(job.get('employer_id'))
                    app_with_details['employer_name'] = employer.get('name') if employer else 'Unknown Employer'
                    
                    # Set status color for UI display
                    status = application.get('status', 'pending')
                    if status == 'pending':
                        app_with_details['status_color'] = 'warning'
                    elif status == 'accepted':
                        app_with_details['status_color'] = 'success'
                    elif status == 'rejected':
                        app_with_details['status_color'] = 'danger'
                    else:
                        app_with_details['status_color'] = 'secondary'
                    
                    worker_applications.append(app_with_details)
        
        if hasattr(user, 'applications'):
            user['applications'] = worker_applications
        else:
            user = dict(user)
            user['applications'] = worker_applications
            
        return render_template('worker_dashboard.html', user=user, recommended_jobs=recommended_jobs)
    else:
        # For employers, show their posted jobs and recommended workers
        posted_jobs = [job for job in jobs.values() if job.get('employer_id') == user_id]
        recommended_workers = recommendation_service.get_recommended_workers(user_id)
        
        # Create sample hiring activity for UI display
        hiring_activity = []
        for job in posted_jobs[:3]:  # Use most recent jobs for activity
            hiring_activity.append({
                'icon': 'clipboard-plus',
                'color': 'primary',
                'title': f"Job Posted: {job.get('title')}",
                'description': f"You posted a new job with {len(job.get('skills_required', []))} required skills",
                'date': job.get('created_at', '')[:10]  # Just the date part
            })
            
            # Add application notifications if there are any
            for application in job.get('applications', [])[:2]:  # Show just a couple applications per job
                worker = auth_service.get_user_by_id(application.get('worker_id'))
                if worker:
                    hiring_activity.append({
                        'icon': 'person-check',
                        'color': 'success',
                        'title': f"New Application: {worker.get('name')}",
                        'description': f"Applied for {job.get('title')}",
                        'date': application.get('applied_at', '')[:10]  # Just the date part
                    })
        
        return render_template('employer_dashboard.html', user=user, posted_jobs=posted_jobs, 
                              recommended_workers=recommended_workers, hiring_activity=hiring_activity)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = auth_service.get_user_by_id(user_id)
    
    if request.method == 'POST':
        # Update user profile
        updated_user = {
            'name': request.form.get('name'),
            'bio': request.form.get('bio'),
            'location': request.form.get('location'),
            'skills': request.form.getlist('skills'),
            'hourly_rate': request.form.get('hourly_rate'),
            'availability': request.form.get('availability')
        }
        
        auth_service.update_user(user_id, updated_user)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/job/post', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session['user_type'] != 'employer':
        flash('Only employers can post jobs', 'warning')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        job = {
            'id': str(uuid.uuid4()),
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'location': request.form.get('location'),
            'skills_required': request.form.getlist('skills_required'),
            'pay_rate': request.form.get('pay_rate'),
            'duration': request.form.get('duration'),
            'employer_id': session['user_id'],
            'status': 'open',
            'created_at': datetime.datetime.now().isoformat(),
            'applications': []
        }
        
        jobs[job['id']] = job
        flash('Job posted successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('job_post.html')

@app.route('/job/search')
def search_jobs():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    search_term = request.args.get('search', '')
    location = request.args.get('location', '')
    
    filtered_jobs = []
    for job in jobs.values():
        if job['status'] == 'open':
            if (search_term.lower() in job['title'].lower() or 
                search_term.lower() in job['description'].lower()):
                if not location or location.lower() in job['location'].lower():
                    filtered_jobs.append(job)
    
    if location:
        # Use location service to sort by proximity
        filtered_jobs = location_service.sort_by_proximity(filtered_jobs, location)
    
    return render_template('job_search.html', jobs=filtered_jobs, search_term=search_term, location=location)

@app.route('/job/<job_id>')
def view_job(job_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    job = jobs.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('dashboard'))
    
    employer = auth_service.get_user_by_id(job['employer_id'])
    
    return render_template('job_detail.html', job=job, employer=employer)

@app.route('/job/<job_id>/apply', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session or session['user_type'] != 'worker':
        flash('Only workers can apply for jobs', 'warning')
        return redirect(url_for('dashboard'))
    
    job = jobs.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    
    # Check if already applied
    for application in job['applications']:
        if application['worker_id'] == user_id:
            flash('You have already applied for this job', 'warning')
            return redirect(url_for('view_job', job_id=job_id))
    
    application = {
        'worker_id': user_id,
        'status': 'pending',
        'applied_at': datetime.datetime.now().isoformat()
    }
    
    job['applications'].append(application)
    flash('Application submitted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/job/<job_id>/applications')
def view_applications(job_id):
    if 'user_id' not in session or session['user_type'] != 'employer':
        flash('Only employers can view applications', 'warning')
        return redirect(url_for('dashboard'))
    
    job = jobs.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('dashboard'))
    
    if job['employer_id'] != session['user_id']:
        flash('You can only view applications for your own jobs', 'warning')
        return redirect(url_for('dashboard'))
    
    applications = []
    for application in job['applications']:
        worker = auth_service.get_user_by_id(application['worker_id'])
        if worker:
            applications.append({
                'worker': worker,
                'status': application['status'],
                'applied_at': application['applied_at']
            })
    
    return render_template('applications.html', job=job, applications=applications)

@app.route('/messages')
def messages_view():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_messages = message_service.get_user_messages(user_id)
    
    # Group messages by conversation partner
    conversations = {}
    for msg in user_messages:
        other_user_id = msg['sender_id'] if msg['receiver_id'] == user_id else msg['receiver_id']
        if other_user_id not in conversations:
            other_user = auth_service.get_user_by_id(other_user_id)
            conversations[other_user_id] = {
                'user': other_user,
                'messages': []
            }
        conversations[other_user_id]['messages'].append(msg)
    
    # Sort messages in each conversation by timestamp
    for conv in conversations.values():
        conv['messages'].sort(key=lambda x: x['timestamp'])
    
    return render_template('messages.html', conversations=conversations)

@app.route('/messages/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.form
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        return jsonify({'error': 'Missing required fields'}), 400
    
    message = message_service.send_message(sender_id, receiver_id, content)
    return jsonify({'message': 'Message sent successfully', 'message_data': message}), 200

@app.route('/rate/<user_id>', methods=['POST'])
def rate_user(user_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    rater_id = session['user_id']
    if rater_id == user_id:
        flash('You cannot rate yourself', 'warning')
        return redirect(url_for('dashboard'))
    
    rating_value = int(request.form.get('rating', 5))
    job_id = request.form.get('job_id')
    comment = request.form.get('comment', '')
    
    rating_service.add_rating(rater_id, user_id, rating_value, comment, job_id)
    flash('Rating submitted successfully', 'success')
    return redirect(url_for('view_profile', user_id=user_id))

@app.route('/profile/<user_id>')
def view_profile(user_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard'))
    
    user_ratings = rating_service.get_user_ratings(user_id)
    average_rating = rating_service.calculate_average_rating(user_id)
    
    return render_template('profile_view.html', user=user, ratings=user_ratings, average_rating=average_rating)

@app.route('/api/search/workers')
def search_workers_api():
    if 'user_id' not in session or session['user_type'] != 'employer':
        return jsonify({'error': 'Authentication required'}), 401
    
    search_term = request.args.get('search', '')
    skills = request.args.getlist('skills')
    location = request.args.get('location', '')
    
    # Filter workers
    filtered_workers = []
    for user in users.values():
        if user['user_type'] == 'worker':
            if (not search_term or search_term.lower() in user['name'].lower() or 
                (user.get('bio') and search_term.lower() in user['bio'].lower())):
                
                if not skills or any(skill in user.get('skills', []) for skill in skills):
                    if not location or location.lower() in user.get('location', '').lower():
                        filtered_workers.append(user)
    
    if location:
        # Use location service to sort by proximity
        filtered_workers = location_service.sort_workers_by_proximity(filtered_workers, location)
    
    # Remove sensitive information
    safe_workers = []
    for worker in filtered_workers:
        safe_worker = {k: v for k, v in worker.items() if k != 'password'}
        safe_worker['average_rating'] = rating_service.calculate_average_rating(worker['id'])
        safe_workers.append(safe_worker)
    
    return jsonify({'workers': safe_workers})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
