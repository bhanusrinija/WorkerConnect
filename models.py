# Define data models for the application
# Since we're using in-memory storage for this MVP, these are just template structures
# In a production environment, these would be SQLAlchemy or other ORM models

class User:
    """Template model for User data"""
    def __init__(self, id, name, email, password, user_type):
        self.id = id  # UUID string
        self.name = name
        self.email = email
        self.password = password  # Hashed password
        self.user_type = user_type  # 'worker' or 'employer'
        self.created_at = None  # Timestamp
        self.location = None  # Location string
        self.bio = None  # Text description
        self.profile_pic = None  # URL to profile picture
        self.skills = []  # List of skill IDs for workers
        self.verified = False  # Profile verification status
        self.contact_info = {}  # Dictionary of contact information
        self.hourly_rate = None  # For workers
        self.availability = None  # For workers
        self.company_name = None  # For employers
        self.company_website = None  # For employers
        self.company_description = None  # For employers

class Job:
    """Template model for Job data"""
    def __init__(self, id, title, description, employer_id):
        self.id = id  # UUID string
        self.title = title
        self.description = description
        self.employer_id = employer_id  # Reference to employer's user ID
        self.created_at = None  # Timestamp
        self.updated_at = None  # Timestamp
        self.location = None  # Location string
        self.skills_required = []  # List of skill IDs
        self.pay_rate = None  # Pay rate or range
        self.duration = None  # Job duration
        self.status = 'open'  # 'open', 'filled', 'closed'
        self.applications = []  # List of application objects
        self.views = 0  # View count for analytics

class Skill:
    """Template model for Skill data"""
    def __init__(self, id, name, category):
        self.id = id  # UUID string
        self.name = name
        self.category = category
        self.description = None

class Message:
    """Template model for Message data"""
    def __init__(self, id, sender_id, receiver_id, content):
        self.id = id  # UUID string
        self.sender_id = sender_id  # Reference to sender's user ID
        self.receiver_id = receiver_id  # Reference to receiver's user ID
        self.content = content
        self.timestamp = None  # Timestamp
        self.read = False  # Whether the message has been read

class Rating:
    """Template model for Rating data"""
    def __init__(self, id, rater_id, rated_user_id, rating, comment=None, job_id=None):
        self.id = id  # UUID string
        self.rater_id = rater_id  # Reference to rater's user ID
        self.rated_user_id = rated_user_id  # Reference to rated user's ID
        self.rating = rating  # Numeric rating (1-5)
        self.comment = comment  # Text comment
        self.timestamp = None  # Timestamp
        self.job_id = job_id  # Reference to related job (optional)
