import bcrypt
import os
import datetime
from sqlalchemy.orm import Session as DbSession
from db.models import User, Session # Assuming models are in db/models.py

# This would be your actual database session, configured elsewhere
# For now, we'll use a placeholder or assume it's passed to functions.
# from db.database import SessionLocal # Example if you have a db setup file

# Placeholder for database interaction.
# In a real app, you'd use a SQLAlchemy session to interact with the DB.
# For now, these functions might print to console or use in-memory structures.
IN_MEMORY_USERS = {}
IN_MEMORY_SESSIONS = {}

def hash_password(password: str) -> bytes:
    """Hashes a plain text password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verifies a plain text password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def create_user(username: str, email: str, password: str, db: DbSession = None):
    """Hashes the password and stores the new user."""
    password_hash = hash_password(password)
    if db:
        new_user = User(username=username, email=email, password_hash=password_hash.decode('utf-8'))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        # Placeholder if no DB session
        print(f"Placeholder: Creating user {username} with email {email}")
        IN_MEMORY_USERS[username] = {"email": email, "password_hash": password_hash.decode('utf-8')}
        return IN_MEMORY_USERS[username]

def authenticate_user(username: str, password: str, db: DbSession = None):
    """Fetches a user by username and verifies the password."""
    if db:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash.encode('utf-8')):
            return user
        return None
    else:
        # Placeholder if no DB session
        user_data = IN_MEMORY_USERS.get(username)
        if user_data and verify_password(password, user_data["password_hash"].encode('utf-8')):
            print(f"Placeholder: Authenticated user {username}")
            return user_data
        print(f"Placeholder: Authentication failed for user {username}")
        return None

def create_session(user_id: int, db: DbSession = None):
    """
    Generates a secure session ID, calculates an expiry time, and stores the session.
    TODO: Implement session regeneration upon login to prevent session fixation.
          This means invalidating any old session and creating a new one when a user logs in.
    """
    session_id = os.urandom(16).hex()
    # Example: session expires in 1 hour
    expiry_timestamp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    if db:
        new_session = Session(session_id=session_id, user_id=user_id, expiry_timestamp=expiry_timestamp)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session.session_id
    else:
        # Placeholder if no DB session
        print(f"Placeholder: Creating session {session_id} for user_id {user_id}")
        IN_MEMORY_SESSIONS[session_id] = {"user_id": user_id, "expiry_timestamp": expiry_timestamp}
        return session_id

def get_session(session_id: str, db: DbSession = None):
    """Retrieves a session by its ID if it exists and has not expired."""
    if db:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        if session and session.expiry_timestamp > datetime.datetime.utcnow():
            return session
        return None
    else:
        # Placeholder if no DB session
        session_data = IN_MEMORY_SESSIONS.get(session_id)
        if session_data and session_data["expiry_timestamp"] > datetime.datetime.utcnow():
            print(f"Placeholder: Session {session_id} is valid.")
            return session_data
        print(f"Placeholder: Session {session_id} is invalid or expired.")
        return None

def delete_session(session_id: str, db: DbSession = None):
    """Deletes/invalidates a session."""
    if db:
        session = db.query(Session).filter(Session.session_id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    else:
        # Placeholder if no DB session
        if session_id in IN_MEMORY_SESSIONS:
            del IN_MEMORY_SESSIONS[session_id]
            print(f"Placeholder: Deleted session {session_id}")
            return True
        print(f"Placeholder: Session {session_id} not found for deletion.")
        return False
