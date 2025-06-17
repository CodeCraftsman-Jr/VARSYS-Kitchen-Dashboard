# Firebase integration for Kitchen Dashboard

import os
import json
import pandas as pd
from datetime import datetime
import requests

# Firebase Admin SDK with fallback for missing modules
FIREBASE_ADMIN_AVAILABLE = False
firebase_admin = None
credentials = None
firestore = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_ADMIN_AVAILABLE = True
    print("Firebase Admin SDK imported successfully")
except ImportError as e:
    print(f"Firebase Admin SDK not available: {e}")
    print("Application will run in offline mode only")

# Import logger if available
try:
    from modules.firebase_logger import log_info, log_warning, log_error
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    # Fallback logging functions
    def log_info(message):
        print(f"INFO: {message}")
    def log_warning(message):
        print(f"WARNING: {message}")
    def log_error(message, exception=None):
        print(f"ERROR: {message}")
        if exception:
            print(f"Exception details: {str(exception)}")

# For user authentication - Enhanced import check for frozen applications
PYREBASE_AVAILABLE = False
pyrebase = None

try:
    # Fix httplib2 circular import issue BEFORE importing pyrebase
    try:
        import socks
        import httplib2.socks
        log_info("SOCKS and httplib2.socks modules loaded successfully")
    except ImportError as socks_error:
        log_warning(f"SOCKS modules not available: {socks_error}")

    import pyrebase
    PYREBASE_AVAILABLE = True
    log_info("Pyrebase imported successfully")
except ImportError as e:
    log_warning(f"Pyrebase import failed: {e}")
    # Try alternative import methods for frozen applications
    try:
        import sys
        import importlib

        # Try to fix httplib2 issue first
        try:
            importlib.import_module('socks')
            importlib.import_module('httplib2.socks')
            log_info("SOCKS modules loaded via importlib")
        except:
            log_warning("Could not load SOCKS modules via importlib")

        pyrebase = importlib.import_module('pyrebase')
        PYREBASE_AVAILABLE = True
        log_info("Pyrebase imported successfully using importlib")
    except Exception as e2:
        log_warning(f"Alternative pyrebase import also failed: {e2}")
        # Check if we're in a frozen environment and pyrebase might be available
        if hasattr(sys, 'frozen'):
            log_info("Running in frozen environment - attempting pyrebase fallback")
            try:
                # Try to find pyrebase in the library
                import os
                lib_path = os.path.join(os.path.dirname(sys.executable), 'lib')
                pyrebase_path = os.path.join(lib_path, 'pyrebase')
                if os.path.exists(pyrebase_path):
                    log_info("Pyrebase library found in frozen app - marking as available")
                    PYREBASE_AVAILABLE = True
                    # Set pyrebase to None so it can be imported later when needed
                    pyrebase = None
                else:
                    log_warning("Pyrebase library not found in frozen app")
            except Exception as e3:
                log_warning(f"Frozen environment pyrebase check failed: {e3}")

        if not PYREBASE_AVAILABLE:
            log_warning("Pyrebase is not available. User authentication will not work.")

# Global variables
FIREBASE_APP = None
FIRESTORE_DB = None
FIREBASE_AUTH = None

# Define the path to the credentials files
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
credentials_path = os.path.join(current_dir, "firebase_credentials.json")
web_config_path = os.path.join(current_dir, "firebase_web_config.json")

# Firebase is considered available if both credential files exist
FIREBASE_AVAILABLE = os.path.exists(credentials_path) and os.path.exists(web_config_path)

# Data synchronization functions
def sync_data_to_firebase(user_id, data_dir):
    """
    Sync data from local CSV files to Firebase Firestore
    
    Args:
        user_id (str): User ID to store data under
        data_dir (str): Directory containing CSV files
        
    Returns:
        bool: True if sync was successful, False otherwise
    """
    global FIRESTORE_DB
    
    if not FIRESTORE_DB:
        log_error("Firestore database is not initialized")
        return False
    
    try:
        log_info(f"Starting sync to Firebase for user: {user_id}")
        
        # Get list of CSV files in the data directory
        if not os.path.exists(data_dir):
            log_error(f"Data directory not found: {data_dir}")
            return False
            
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            log_warning(f"No CSV files found in directory: {data_dir}")
            return False
            
        # Reference to the user's data collection
        user_ref = FIRESTORE_DB.collection('users').document(user_id)
        
        # Create user document if it doesn't exist
        if not user_ref.get().exists:
            user_ref.set({
                'email': user_id if '@' in user_id else f"{user_id}@kitchen-dashboard.app",
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_sync': firestore.SERVER_TIMESTAMP
            })
            log_info(f"Created new user document for: {user_id}")
        
        # Upload each CSV file as a collection
        for csv_file in csv_files:
            collection_name = os.path.splitext(csv_file)[0]  # Remove .csv extension
            file_path = os.path.join(data_dir, csv_file)
            
            try:
                # Read CSV file
                df = pd.read_csv(file_path)
                
                # Skip empty dataframes
                if df.empty:
                    log_info(f"Skipping empty dataframe: {collection_name}")
                    continue
                
                # Convert dataframe to list of dictionaries
                records = df.to_dict('records')
                
                # Delete existing collection
                collection_ref = user_ref.collection(collection_name)
                delete_collection(collection_ref, 10)
                
                # Upload new data
                batch = FIRESTORE_DB.batch()
                batch_count = 0
                batch_size = 500  # Firestore batch size limit
                
                for i, record in enumerate(records):
                    # Convert any NaN values to None
                    record = {k: (None if pd.isna(v) else v) for k, v in record.items()}
                    
                    # Add document to batch
                    doc_ref = collection_ref.document(f"doc_{i}")
                    batch.set(doc_ref, record)
                    batch_count += 1
                    
                    # Commit batch when it reaches the limit
                    if batch_count >= batch_size:
                        batch.commit()
                        log_info(f"Committed batch of {batch_count} documents for {collection_name}")
                        batch = FIRESTORE_DB.batch()
                        batch_count = 0
                
                # Commit any remaining documents
                if batch_count > 0:
                    batch.commit()
                    log_info(f"Committed final batch of {batch_count} documents for {collection_name}")
                
                log_info(f"Successfully uploaded {len(records)} records for {collection_name}")
                
            except Exception as e:
                log_error(f"Error uploading {csv_file}", e)
                continue
        
        # Update last sync timestamp
        user_ref.update({
            'last_sync': firestore.SERVER_TIMESTAMP
        })
        
        log_info(f"Successfully synced all data to Firebase for user: {user_id}")
        return True
        
    except Exception as e:
        log_error("Error in sync_data_to_firebase", e)
        return False

def sync_data_from_firebase(user_id, data_dir):
    """
    Sync data from Firebase Firestore to local CSV files
    
    Args:
        user_id (str): User ID to retrieve data for
        data_dir (str): Directory to store CSV files
        
    Returns:
        bool: True if sync was successful, False otherwise
    """
    global FIRESTORE_DB
    
    if not FIRESTORE_DB:
        log_error("Firestore database is not initialized")
        return False
    
    try:
        log_info(f"Starting sync from Firebase for user: {user_id}")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            log_info(f"Created data directory: {data_dir}")
        
        # Reference to the user's data collection
        user_ref = FIRESTORE_DB.collection('users').document(user_id)
        
        # Check if user document exists
        if not user_ref.get().exists:
            log_error(f"User document not found for: {user_id}")
            return False
        
        # Get all collections for the user
        collections = user_ref.collections()
        collection_count = 0
        
        for collection in collections:
            collection_name = collection.id
            
            try:
                # Get all documents in the collection
                docs = collection.stream()
                records = [doc.to_dict() for doc in docs]
                
                # Skip empty collections
                if not records:
                    log_info(f"Skipping empty collection: {collection_name}")
                    continue
                
                # Convert to dataframe
                df = pd.DataFrame(records)
                
                # Save to CSV
                file_path = os.path.join(data_dir, f"{collection_name}.csv")
                df.to_csv(file_path, index=False)
                
                log_info(f"Successfully downloaded {len(records)} records for {collection_name}")
                collection_count += 1
                
            except Exception as e:
                log_error(f"Error downloading {collection_name}", e)
                continue
        
        if collection_count == 0:
            log_warning(f"No collections found for user: {user_id}")
            return False
        
        log_info(f"Successfully synced {collection_count} collections from Firebase for user: {user_id}")
        return True
        
    except Exception as e:
        log_error("Error in sync_data_from_firebase", e)
        return False

# Authentication functions
def sign_in_with_email(email, password):
    """
    Sign in with email and password
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        dict: User information if successful, None otherwise
    """
    global FIREBASE_AUTH
    
    # Log the authentication attempt
    log_info(f"Attempting to sign in user: {email}")
    
    # Check if Firebase Auth is available
    if not FIREBASE_AUTH or not PYREBASE_AVAILABLE:
        log_error("Firebase Auth is not initialized")
        return None
    
    try:
        # Attempt to sign in
        user = FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
        log_info(f"User authenticated successfully: {email}")
        return user
    except requests.exceptions.HTTPError as e:
        # Parse error message from Firebase
        error_json = e.args[1]
        try:
            error_data = json.loads(error_json)
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            log_error(f"Authentication failed: {error_message}", e)
        except:
            log_error("Authentication failed with unknown error", e)
        return None
    except Exception as e:
        log_error("Authentication failed with exception", e)
        return None

# Delete collection utility function
def delete_collection(coll_ref, batch_size):
    """Delete a collection by batches"""
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def initialize_firebase():
    """Initialize Firebase and check for credentials file"""
    global FIREBASE_APP, FIRESTORE_DB, FIREBASE_AUTH, FIREBASE_AVAILABLE
    
    # Get the absolute path to the project root directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Look for Firebase credentials file in multiple locations
    credentials_paths = [
        os.path.join(current_dir, "firebase_credentials.json"),
        os.path.join(current_dir, "secure_credentials", "firebase_credentials.json")
    ]

    # Log the initialization process
    log_info("Initializing Firebase integration...")

    credentials_path = None
    for path in credentials_paths:
        log_info(f"Looking for credentials at: {path}")
        if os.path.exists(path):
            credentials_path = path
            log_info(f"Found Firebase credentials at: {path}")
            break

    # Check if the credentials file exists
    if not credentials_path:
        log_error("Firebase credentials file not found in any of these locations:")
        for path in credentials_paths:
            log_error(f"  - {path}")
        FIREBASE_AVAILABLE = False
        return False
    
    # Check if Firebase Admin SDK is available - FALLBACK FOR BUILD ENVIRONMENT
    if not FIREBASE_ADMIN_AVAILABLE:
        log_warning("Firebase Admin SDK not available - trying Pyrebase-only mode")

        # Try to initialize with Pyrebase only (for build environments)
        if PYREBASE_AVAILABLE:
            return initialize_pyrebase_only_mode()
        else:
            log_error("Neither Firebase Admin SDK nor Pyrebase is available")
            log_error("To enable Firebase features, install: pip install firebase-admin pyrebase4")
            FIREBASE_AVAILABLE = False
            return False

    try:
        # Load the Firebase service account credentials for Admin SDK
        log_info("Loading Firebase credentials...")
        log_info(f"Using credentials file: {credentials_path}")

        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            log_info("Initializing Firebase Admin SDK...")
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)

        # Get Firestore database instance
        log_info("Getting Firestore database instance...")
        FIRESTORE_DB = firestore.client()
        
        # Initialize Pyrebase for authentication if available
        if PYREBASE_AVAILABLE:
            # Try to load from main firebase_config.json first
            main_config_path = os.path.join(current_dir, "firebase_config.json")
            web_config = None

            if os.path.exists(main_config_path):
                try:
                    log_info(f"Loading main Firebase config from: {main_config_path}")
                    with open(main_config_path, 'r') as f:
                        main_config = json.load(f)

                    firebase_config = main_config.get('firebase', {})
                    if firebase_config and firebase_config.get('apiKey') and firebase_config.get('projectId'):
                        web_config = firebase_config
                        log_info("Using Firebase config from main configuration file")
                    else:
                        log_warning("Main Firebase config is invalid or incomplete")
                except Exception as e:
                    log_error(f"Error loading main Firebase config: {e}")

            # Fallback to web config files only if main config is not available
            if not web_config:
                web_config_paths = [
                    os.path.join(current_dir, "firebase_web_config.json"),
                    os.path.join(current_dir, "secure_credentials", "firebase_web_config.json")
                ]

                for path in web_config_paths:
                    if os.path.exists(path):
                        try:
                            log_info(f"Loading Firebase web config from: {path}")
                            with open(path, 'r') as f:
                                config = json.load(f)

                            if config and config.get('apiKey') and config.get('projectId'):
                                web_config = config
                                break
                            else:
                                log_warning(f"Invalid Firebase config in {path}")
                        except Exception as e:
                            log_error(f"Error loading Firebase config from {path}: {e}")

            if web_config:
                try:
                    log_info("Initializing Pyrebase for authentication...")
                    # Ensure pyrebase is imported if not already
                    global pyrebase
                    if pyrebase is None:
                        import pyrebase as pyrebase_module
                        pyrebase = pyrebase_module
                    FIREBASE_APP = pyrebase.initialize_app(web_config)
                    FIREBASE_AUTH = FIREBASE_APP.auth()
                    log_info("Pyrebase authentication initialized successfully")
                except Exception as e:
                    log_error(f"Failed to initialize Pyrebase: {e}")
                    log_warning("Falling back to Firebase Admin SDK only")
                    FIREBASE_AUTH = None
            else:
                log_error("No valid Firebase web configuration found")
                log_error("Authentication will not work without valid web config")
                FIREBASE_AVAILABLE = False
                return False
        else:
            log_warning("Pyrebase not available, user authentication will not work.")
            FIREBASE_AVAILABLE = False
            return False
        
        # Set global flag that Firebase is available
        FIREBASE_AVAILABLE = True
        log_info("Firebase initialization successful!")
        
        return True
    except Exception as e:
        log_error("Failed to initialize Firebase", e)
        FIREBASE_AVAILABLE = False
        return False

def initialize_pyrebase_only_mode():
    """Initialize Firebase using only Pyrebase (fallback for build environments)"""
    global FIREBASE_APP, FIRESTORE_DB, FIREBASE_AUTH, FIREBASE_AVAILABLE

    try:
        log_info("Attempting Pyrebase-only initialization...")

        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir.endswith('modules'):
            current_dir = os.path.dirname(current_dir)

        # Try to load Firebase web config for Pyrebase
        web_config = None
        web_config_paths = [
            os.path.join(current_dir, "firebase_config.json"),
            os.path.join(current_dir, "firebase_web_config.json"),
            os.path.join(current_dir, "secure_credentials", "firebase_web_config.json")
        ]

        for path in web_config_paths:
            if os.path.exists(path):
                try:
                    log_info(f"Loading Firebase config from: {path}")
                    with open(path, 'r') as f:
                        config = json.load(f)

                    # Handle nested firebase config
                    if 'firebase' in config:
                        config = config['firebase']

                    if config and config.get('apiKey') and config.get('projectId'):
                        web_config = config
                        log_info(f"Valid Firebase config found in: {path}")
                        break
                    else:
                        log_warning(f"Invalid Firebase config in {path}")
                except Exception as e:
                    log_error(f"Error loading Firebase config from {path}: {e}")

        if not web_config:
            log_error("No valid Firebase web configuration found for Pyrebase-only mode")
            FIREBASE_AVAILABLE = False
            return False

        # Initialize Pyrebase
        try:
            global pyrebase
            if pyrebase is None:
                import pyrebase as pyrebase_module
                pyrebase = pyrebase_module

            FIREBASE_APP = pyrebase.initialize_app(web_config)
            FIREBASE_AUTH = FIREBASE_APP.auth()

            # Use Realtime Database instead of Firestore for Pyrebase-only mode
            try:
                FIRESTORE_DB = FIREBASE_APP.database()
                log_info("Firebase Realtime Database initialized (Pyrebase-only mode)")
            except Exception as e:
                log_warning(f"Realtime Database initialization failed: {e}")
                FIRESTORE_DB = None

            FIREBASE_AVAILABLE = True
            log_info("Pyrebase-only mode initialization successful!")
            return True

        except Exception as e:
            log_error(f"Failed to initialize Pyrebase: {e}")
            FIREBASE_AVAILABLE = False
            return False

    except Exception as e:
        log_error(f"Pyrebase-only mode initialization failed: {e}")
        FIREBASE_AVAILABLE = False
        return False

def initialize_firebase_with_config(firebase_config):
    """Initialize Firebase with provided configuration dictionary for v1.0.6"""
    global FIREBASE_APP, FIRESTORE_DB, FIREBASE_AUTH, FIREBASE_AVAILABLE

    try:
        # Check if pyrebase is available
        if not PYREBASE_AVAILABLE:
            log_error("Pyrebase is not available. Please install pyrebase4.")
            FIREBASE_AVAILABLE = False
            return False

        # Validate configuration more strictly
        if not firebase_config:
            log_error("No Firebase configuration provided")
            FIREBASE_AVAILABLE = False
            return False

        required_fields = ['apiKey', 'authDomain', 'projectId']
        missing_fields = []

        for field in required_fields:
            if not firebase_config.get(field) or firebase_config.get(field).strip() == '':
                missing_fields.append(field)

        if missing_fields:
            log_error(f"Invalid Firebase configuration - missing required fields: {', '.join(missing_fields)}")
            FIREBASE_AVAILABLE = False
            return False

        log_info("Initializing Firebase with provided configuration...")

        # Initialize Pyrebase app with provided config
        try:
            # Ensure pyrebase is imported if not already
            global pyrebase
            if pyrebase is None:
                import pyrebase as pyrebase_module
                pyrebase = pyrebase_module
            FIREBASE_APP = pyrebase.initialize_app(firebase_config)
            FIREBASE_AUTH = FIREBASE_APP.auth()
        except Exception as e:
            log_error(f"Failed to initialize Pyrebase with config: {e}")
            FIREBASE_AVAILABLE = False
            return False

        # Initialize Firestore database (if available)
        try:
            FIRESTORE_DB = FIREBASE_APP.database()
            log_info("Firebase Realtime Database initialized successfully with provided config")
        except Exception as e:
            log_warning(f"Firebase Realtime Database initialization failed: {e}")
            FIRESTORE_DB = None

        # Set global flag that Firebase is available
        FIREBASE_AVAILABLE = True
        log_info("Firebase initialization successful with provided config!")

        return True
    except Exception as e:
        log_error("Failed to initialize Firebase with provided config", e)
        FIREBASE_AVAILABLE = False
        return False

def sign_in_with_email(email, password):
    """Sign in user with email and password for v1.0.6 with improved error handling"""
    if not FIREBASE_AVAILABLE or not FIREBASE_AUTH:
        log_error("Firebase authentication is not available")
        return None

    try:
        log_info(f"Attempting to sign in user: {email}")
        user = FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
        log_info("User authentication successful!")
        return user
    except requests.exceptions.HTTPError as e:
        # Parse detailed error message from Firebase
        error_json = e.args[1] if len(e.args) > 1 else "{}"
        try:
            import json
            error_data = json.loads(error_json)
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            log_error(f"Authentication failed for user {email}: {error_message}")

            # Log specific error details for debugging
            if "INVALID_LOGIN_CREDENTIALS" in error_message:
                log_error("Invalid email or password provided")
            elif "EMAIL_NOT_FOUND" in error_message:
                log_error("No user account found with this email")
            elif "INVALID_PASSWORD" in error_message:
                log_error("Incorrect password")
            elif "USER_DISABLED" in error_message:
                log_error("User account has been disabled")

        except:
            log_error(f"Authentication failed for user: {email} with HTTP error", e)
        return None
    except Exception as e:
        log_error(f"Authentication failed for user: {email}", e)
        return None

def authenticate_user(email, password):
    """Authenticate a user with Firebase"""
    if not FIREBASE_AVAILABLE or not PYREBASE_AVAILABLE:
        log_error("Firebase or Pyrebase is not available. Cannot authenticate user.")
        return None

    try:
        log_info(f"Authenticating user: {email}")
        # Sign in the user
        user = FIREBASE_AUTH.sign_in_with_email_and_password(email, password)
        log_info("User authentication successful!")
        return user
    except Exception as e:
        log_error(f"Authentication failed for user: {email}", e)
        return None


def change_user_password(id_token, new_password):
    """Change user password using Firebase Auth REST API"""
    if not FIREBASE_AVAILABLE or not FIREBASE_APP:
        log_error("Firebase is not available. Cannot change password.")
        return False

    try:
        import requests

        # Get API key from Firebase app configuration
        api_key = None
        if hasattr(FIREBASE_APP, 'api_key'):
            api_key = FIREBASE_APP.api_key
        else:
            # Try to get from config if available
            try:
                config = FIREBASE_APP.config
                api_key = config.get('apiKey', '')
            except:
                log_error("Could not retrieve API key from Firebase configuration")
                return False

        if not api_key:
            log_error("Firebase API key not available")
            return False

        # Firebase Auth REST API endpoint for changing password
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"

        payload = {
            "idToken": id_token,
            "password": new_password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            log_info("Password changed successfully")
            return True
        else:
            log_error(f"Failed to change password: {response.text}")
            return False

    except Exception as e:
        log_error(f"Error changing password", e)
        return False

def get_user_data(user_id, data_type):
    """Get user data from Firestore"""
    if not FIREBASE_AVAILABLE:
        log_error("Firebase is not available. Cannot get user data.")
        return None
    
    try:
        log_info(f"Getting {data_type} data for user: {user_id}")
        # Get a reference to the user's data collection
        user_ref = FIRESTORE_DB.collection("users").document(user_id).collection(data_type)
        
        # Get all documents in the collection
        docs = user_ref.stream()
        
        # Convert to list of dictionaries
        data = [doc.to_dict() for doc in docs]
        
        log_info(f"Successfully retrieved {len(data)} {data_type} records for user: {user_id}")
        return data
    except Exception as e:
        log_error(f"Failed to get {data_type} data for user: {user_id}", e)
        return None

def save_user_data(user_id, data_type, data):
    """Save user data to Firestore"""
    if not FIREBASE_AVAILABLE:
        log_error("Firebase is not available. Cannot save user data.")
        return False
    
    try:
        log_info(f"Saving {data_type} data for user: {user_id}")
        
        # Create a timestamp
        timestamp = datetime.now().isoformat()
        
        # Save data to Firestore
        FIRESTORE_DB.collection("users").document(user_id).collection(data_type).document(timestamp).set(data)
        
        log_info(f"Successfully saved {data_type} data for user: {user_id}")
        return True
    except Exception as e:
        log_error(f"Failed to save {data_type} data for user: {user_id}", e)
        return False

def sync_data_to_firebase(user_id, data_dir):
    """Sync local CSV data to Firebase"""
    if not FIREBASE_AVAILABLE:
        log_error("Firebase is not available. Cannot sync data to Firebase.")
        return False
    
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        log_error(f"Data directory not found: {data_dir}")
        return False
    
    try:
        log_info(f"Syncing data to Firebase for user: {user_id} from directory: {data_dir}")
        
        # For each data file, store in Firebase
        files_synced = 0
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                # Parse file name (remove extension)
                collection_name = os.path.splitext(filename)[0]
                filepath = os.path.join(data_dir, filename)
                
                log_info(f"Processing file: {filename} for collection: {collection_name}")
                
                try:
                    # Read CSV file using pandas
                    df = pd.read_csv(filepath, encoding='utf-8')
                    
                    # Convert DataFrame to dict for Firebase
                    data_dict = df.to_dict(orient='records')
                    
                    # Get a reference to the user's collection
                    collection_ref = FIRESTORE_DB.collection("users").document(user_id).collection(collection_name)
                    
                    # Clear existing data (optional)
                    log_info(f"Clearing existing data for collection: {collection_name}")
                    delete_collection(collection_ref, 10)
                    
                    # Save each record with a unique ID
                    for i, record in enumerate(data_dict):
                        collection_ref.document(f"record_{i}").set(record)
                    
                    log_info(f"Successfully synced {len(data_dict)} records for {collection_name}")
                    files_synced += 1
                except Exception as e:
                    log_error(f"Error processing file: {filename}", e)
                    continue
        
        log_info(f"Sync completed. Total files synced: {files_synced}")
        return True
    except Exception as e:
        log_error("Failed to sync data to Firebase", e)
        return False

def sync_data_from_firebase(user_id, data_dir):
    """Sync data from Firebase to local CSV files"""
    if not FIREBASE_AVAILABLE:
        log_error("Firebase is not available. Cannot sync data from Firebase.")
        return False
    
    if not os.path.exists(data_dir):
        log_info(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir)
    
    try:
        log_info(f"Syncing data from Firebase for user: {user_id} to directory: {data_dir}")
        
        # Get all collections for the user
        user_ref = FIRESTORE_DB.collection("users").document(user_id)
        collections = user_ref.collections()
        
        collections_synced = 0
        
        # For each collection, fetch data and save to CSV
        for collection in collections:
            collection_name = collection.id
            log_info(f"Processing collection: {collection_name}")
            
            # Get all documents in the collection
            docs = collection.stream()
            records = [doc.to_dict() for doc in docs]
            
            if not records:
                log_warning(f"No records found in collection: {collection_name}")
                continue
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Save to CSV
            csv_path = os.path.join(data_dir, f"{collection_name}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            log_info(f"Successfully saved {len(records)} records to {csv_path}")
            collections_synced += 1
        
        log_info(f"Sync completed. Total collections synced: {collections_synced}")
        return True
    except Exception as e:
        log_error("Failed to sync data from Firebase", e)
        return False
