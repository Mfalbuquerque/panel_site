import pytest
import bcrypt
import datetime
from unittest.mock import MagicMock, patch

# Functions to test from app.auth
from app.auth import (
    hash_password,
    verify_password,
    create_user,
    authenticate_user,
    create_session,
    get_session,
    delete_session
)
# Assuming db.models is structured as in previous steps
from db.models import User, Session as DBSession # Renamed to avoid clash with sqlalchemy.orm.Session

# --- Password Hashing and Verification Tests ---
def test_password_hashing():
    """Test that hash_password returns a valid bcrypt hash and verify_password works."""
    password = "securepassword123"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert isinstance(hashed, bytes)
    # Bcrypt hashes typically start with $2b$ (or $2a$, $2y$)
    assert hashed.startswith(b"$2b$") or hashed.startswith(b"$2a$") or hashed.startswith(b"$2y$")
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

# --- User Creation and Authentication Tests (Mocking DB) ---
@pytest.fixture
def mock_db_session():
    """Fixture for a mock SQLAlchemy session."""
    db_session = MagicMock()
    # Configure query, filter, first, add, commit, refresh methods as needed per test
    db_session.query.return_value.filter.return_value.first.return_value = None # Default: user not found
    return db_session

def test_create_user_success(mocker, mock_db_session):
    """Test successful user creation, mocking DB save."""
    mocker.patch('app.auth.hash_password', return_value=b"hashed_password_bytes")
    
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    
    created_user_obj = User(id=1, username=username, email=email, password_hash="hashed_password_bytes")
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh = lambda obj: setattr(obj, 'id', 1) # Simulate refresh setting an ID

    # Patch the User model instantiation if necessary, or ensure the mock_db_session handles it
    with patch('app.auth.User', return_value=created_user_obj) as mock_user_model:
        user = create_user(username, email, password, db=mock_db_session)

    # Assert hash_password was called
    app.auth.hash_password.assert_called_once_with(password)
    
    # Assert DB methods were called
    mock_user_model.assert_called_once_with(username=username, email=email, password_hash='hashed_password_bytes')
    mock_db_session.add.assert_called_once_with(created_user_obj)
    mock_db_session.commit.assert_called_once()
    
    assert user is not None
    assert user.username == username
    assert user.password_hash == "hashed_password_bytes" # Stored as string in model

def test_authenticate_user_success(mocker, mock_db_session):
    """Test successful user authentication."""
    username = "testuser"
    password = "password123"
    hashed_password_str = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    mock_user_instance = User(id=1, username=username, password_hash=hashed_password_str)
    mock_db_session.query(User).filter(User.username == username).first.return_value = mock_user_instance
    
    mocker.patch('app.auth.verify_password', return_value=True)
    
    user = authenticate_user(username, password, db=mock_db_session)
    
    app.auth.verify_password.assert_called_once_with(password, hashed_password_str.encode('utf-8'))
    assert user is not None
    assert user.username == username

def test_authenticate_user_invalid_password(mocker, mock_db_session):
    """Test authentication failure with an invalid password."""
    username = "testuser"
    password = "wrongpassword"
    correct_hashed_password_str = bcrypt.hashpw(b"correct_password", bcrypt.gensalt()).decode('utf-8')

    mock_user_instance = User(id=1, username=username, password_hash=correct_hashed_password_str)
    mock_db_session.query(User).filter(User.username == username).first.return_value = mock_user_instance
    
    mocker.patch('app.auth.verify_password', return_value=False)
    
    user = authenticate_user(username, password, db=mock_db_session)
    
    app.auth.verify_password.assert_called_once_with(password, correct_hashed_password_str.encode('utf-8'))
    assert user is None

def test_authenticate_user_not_found(mocker, mock_db_session):
    """Test authentication failure when the user is not found."""
    username = "nonexistentuser"
    password = "password123"
    
    mock_db_session.query(User).filter(User.username == username).first.return_value = None
    
    user = authenticate_user(username, password, db=mock_db_session)
    
    assert user is None
    app.auth.verify_password.assert_not_called() # verify_password shouldn't be called if user not found

# --- Session Function Tests (Mocking DB) ---

@pytest.fixture
def mock_db_session_for_session():
    """Fixture for a mock SQLAlchemy session tailored for session tests."""
    db_session = MagicMock()
    db_session.query.return_value.filter.return_value.first.return_value = None # Default: session not found
    return db_session

def test_create_session_success(mocker, mock_db_session_for_session):
    """Test successful session creation."""
    user_id = 1
    mock_session_id = "testsessionid123"
    mocker.patch('os.urandom', return_value=b'testsessionbytes') # Makes os.urandom(16).hex() predictable
    
    # Mock the DBSession model instance that will be created and added
    created_db_session_obj = DBSession(id=1, session_id=mock_session_id, user_id=user_id, expiry_timestamp=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    
    mock_db_session_for_session.add.return_value = None
    mock_db_session_for_session.commit.return_value = None
    mock_db_session_for_session.refresh = lambda obj: setattr(obj, 'id', 1)

    with patch('app.auth.Session', return_value=created_db_session_obj) as mock_dbsession_model:
        session_id = create_session(user_id, db=mock_db_session_for_session)

    os.urandom.assert_called_once_with(16)
    mock_dbsession_model.assert_called_once() # Check that Session() was called
    
    # Get the actual call arguments for Session()
    args, kwargs = mock_dbsession_model.call_args
    assert kwargs['session_id'] == b'testsessionbytes'.hex()
    assert kwargs['user_id'] == user_id
    assert isinstance(kwargs['expiry_timestamp'], datetime.datetime)
    
    mock_db_session_for_session.add.assert_called_once_with(created_db_session_obj)
    mock_db_session_for_session.commit.assert_called_once()
    
    assert session_id == b'testsessionbytes'.hex()


def test_get_session_valid(mocker, mock_db_session_for_session):
    """Test retrieving a valid session."""
    session_id = "validsessionid"
    user_id = 1
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    mock_session_instance = DBSession(id=1, session_id=session_id, user_id=user_id, expiry_timestamp=expiry)
    mock_db_session_for_session.query(DBSession).filter(DBSession.session_id == session_id).first.return_value = mock_session_instance
    
    session = get_session(session_id, db=mock_db_session_for_session)
    
    assert session is not None
    assert session.session_id == session_id
    assert session.user_id == user_id

def test_get_session_expired(mocker, mock_db_session_for_session):
    """Test that an expired session returns None."""
    session_id = "expiredsessionid"
    user_id = 1
    # Past expiry time
    expiry = datetime.datetime.utcnow() - datetime.timedelta(hours=1) 
    
    mock_session_instance = DBSession(id=1, session_id=session_id, user_id=user_id, expiry_timestamp=expiry)
    mock_db_session_for_session.query(DBSession).filter(DBSession.session_id == session_id).first.return_value = mock_session_instance
    
    session = get_session(session_id, db=mock_db_session_for_session)
    
    assert session is None

def test_get_session_invalid(mocker, mock_db_session_for_session):
    """Test that a non-existent session returns None."""
    session_id = "invalidsessionid"
    mock_db_session_for_session.query(DBSession).filter(DBSession.session_id == session_id).first.return_value = None
    
    session = get_session(session_id, db=mock_db_session_for_session)
    
    assert session is None

def test_delete_session_success(mocker, mock_db_session_for_session):
    """Test successful session deletion."""
    session_id = "sessiontodelete"
    mock_session_instance = DBSession(id=1, session_id=session_id, user_id=1, expiry_timestamp=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    
    mock_db_session_for_session.query(DBSession).filter(DBSession.session_id == session_id).first.return_value = mock_session_instance
    
    result = delete_session(session_id, db=mock_db_session_for_session)
    
    mock_db_session_for_session.delete.assert_called_once_with(mock_session_instance)
    mock_db_session_for_session.commit.assert_called_once()
    assert result is True

def test_delete_session_not_found(mocker, mock_db_session_for_session):
    """Test deleting a non-existent session."""
    session_id = "sessionnotfound"
    mock_db_session_for_session.query(DBSession).filter(DBSession.session_id == session_id).first.return_value = None
    
    result = delete_session(session_id, db=mock_db_session_for_session)
    
    mock_db_session_for_session.delete.assert_not_called()
    assert result is False

# Note: The placeholder logic in app.auth (using IN_MEMORY_USERS, IN_MEMORY_SESSIONS)
# is not directly tested here as the tests focus on the DB interaction path.
# If you needed to test the placeholder paths, you would do so by NOT passing a db session.
# For example: `user = create_user(username, email, password, db=None)`
# and then check IN_MEMORY_USERS.
# However, these tests assume the primary use case involves a database.
