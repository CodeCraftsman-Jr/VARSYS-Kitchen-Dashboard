# Firebase synchronization class for Kitchen Dashboard

import os
import json
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# Import firebase integration module
from modules import firebase_integration
from modules.firebase_integration import FIREBASE_AVAILABLE, log_info, log_warning, log_error

class FirebaseSync:
    """
    Firebase synchronization class for Kitchen Dashboard application.
    Handles data synchronization between local CSV files and Firebase cloud.
    """
    
    def __init__(self, parent, data=None, data_dir="data"):
        """
        Initialize the Firebase synchronization.
        
        Args:
            parent: Parent widget/window for displaying messages
            data: Data dictionary containing application data
            data_dir: Directory containing CSV data files
        """
        self.parent = parent
        self.data = data
        self.data_dir = data_dir
        self.user = None
        self.log_callbacks = []
        
        # Log initialization details for debugging
        self.log_message(f"FirebaseSync initialized with parent: {parent}")
        self.log_message(f"Data directory set to: {data_dir}")
        
        # Log data initialization status
        if data is None:
            self.log_message("WARNING: Data parameter is None", "warning")
        else:
            self.log_message(f"Data parameter contains {len(data)} items: {', '.join(data.keys())}")
            for key, df in data.items():
                self.log_message(f"Data[{key}] has {len(df)} rows and {len(df.columns)} columns")
        
        # Initialize Firebase
        if FIREBASE_AVAILABLE:
            firebase_integration.initialize_firebase()
    
    def add_log_callback(self, callback):
        """
        Add a callback function for logging messages.
        
        Args:
            callback: Function that takes message and level as parameters
        """
        self.log_callbacks.append(callback)
    
    def log_message(self, message, level="info"):
        """
        Log a message using callbacks and the logging system.
        
        Args:
            message: Message to log
            level: Log level (info, warning, error)
        """
        # Log using firebase_integration logger
        if level == "info":
            log_info(message)
        elif level == "warning":
            log_warning(message)
        elif level == "error":
            log_error(message)
        
        # Call all registered callbacks
        for callback in self.log_callbacks:
            try:
                callback(message, level)
            except Exception as e:
                print(f"Error in log callback: {str(e)}")
    
    def is_firebase_available(self):
        """
        Check if Firebase is available.
        
        Returns:
            bool: True if Firebase is available, False otherwise
        """
        # Get path to credentials file
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        credentials_path = os.path.join(current_dir, "firebase_credentials.json")
        web_config_path = os.path.join(current_dir, "firebase_web_config.json")
        
        # Check if both credential files exist
        creds_exist = os.path.exists(credentials_path)
        web_config_exists = os.path.exists(web_config_path)
        
        # Log the status for debugging
        self.log_message(f"Checking Firebase availability: Credentials: {creds_exist}, Web Config: {web_config_exists}")
        
        # Both files must exist for Firebase to be fully available
        return creds_exist and web_config_exists and FIREBASE_AVAILABLE
        
    def is_authenticated(self):
        """
        Check if user is authenticated.
        
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return hasattr(self, 'user_info') and self.user_info is not None
        
    def handle_login_success(self, user_info):
        """
        Handle successful login
        
        Args:
            user_info (dict): User information from Firebase authentication
        """
        self.log_message(f"Login successful for user: {user_info.get('email', 'unknown')}")
        self.user_info = user_info
        
        # Store the authentication token for future requests
        self.auth_token = user_info.get('idToken')
        
        # Log the successful authentication
        self.log_message("User authenticated successfully")
        
        # Check if we need to sync data from the cloud on login
        # Uncomment this if you want automatic sync on login
        # self.sync_from_cloud(show_message=False)
    
    def show_login_dialog(self):
        """
        Show login dialog for Firebase authentication.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        self.log_message("Showing login dialog")
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Firebase Login")
        layout = QVBoxLayout()
        
        # Email input
        layout.addWidget(QLabel("Email:"))
        email_input = QLineEdit()
        layout.addWidget(email_input)
        
        # Password input
        layout.addWidget(QLabel("Password:"))
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)
        
        # Login button
        login_button = QPushButton("Login")
        layout.addWidget(login_button)
        
        # Result status
        result_label = QLabel("")
        layout.addWidget(result_label)
        
        dialog.setLayout(layout)
        
        # Dialog result
        result = [False]
        
        def on_login():
            email = email_input.text()
            password = password_input.text()
            
            if not email or not password:
                result_label.setText("Please enter email and password")
                return
            
            self.log_message(f"Attempting to authenticate user: {email}")
            try:
                self.user = firebase_integration.authenticate_user(email, password)
                if self.user:
                    self.log_message("Authentication successful", "info")
                    result[0] = True
                    dialog.accept()
                else:
                    self.log_message("Authentication failed", "error")
                    result_label.setText("Authentication failed. Please check credentials.")
            except Exception as e:
                self.log_message(f"Error during authentication: {str(e)}", "error")
                result_label.setText(f"Error: {str(e)}")
        
        login_button.clicked.connect(on_login)
        dialog.exec()
        
        return result[0]
    
    def sync_to_cloud(self, show_message=True):
        """
        Sync data to Firebase cloud storage.
        
        Args:
            show_message: Whether to show success/error messages
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        if not FIREBASE_AVAILABLE:
            self.log_message("Firebase integration is not available", "error")
            if show_message:
                QMessageBox.warning(
                    self.parent,
                    "Firebase Not Available",
                    "Firebase integration is not available. Please run setup_firebase.py first."
                )
            return False
        
        try:
            self.log_message("Starting sync to cloud operation...")
            
            # Debug logging for data state and directory
            self.log_message(f"Data directory: {self.data_dir}")
            
            # Initialize Firebase if not already initialized
            if not firebase_integration.initialize_firebase():
                self.log_message("Failed to initialize Firebase", "error")
                if show_message:
                    QMessageBox.warning(
                        self.parent,
                        "Firebase Error",
                        "Failed to initialize Firebase. Please check your credentials."
                    )
                return False
                
            # If not authenticated, show login dialog
            if not self.is_authenticated():
                self.log_message("User not authenticated, authentication required", "warning")
                if show_message:
                    reply = QMessageBox.question(
                        self.parent,
                        "Authentication Required",
                        "You need to sign in to upload data to the cloud. Would you like to sign in now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.log_message("User agreed to authenticate")
                        if not self.show_login_dialog():
                            self.log_message("Login failed or cancelled by user", "warning")
                            return False
                    else:
                        self.log_message("Authentication declined by user", "warning")
                        return False
                else:
                    self.log_message("Cannot sync without authentication", "error")
                    return False
            
            # Check if data directory exists
            if not os.path.exists(self.data_dir):
                self.log_message(f"Data directory not found: {self.data_dir}", "error")
                if show_message:
                    QMessageBox.warning(
                        self.parent,
                        "Data Directory Not Found",
                        f"The data directory '{self.data_dir}' was not found."
                    )
                return False
            
            # Check if there are any CSV files
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            if not csv_files:
                self.log_message("No CSV files found in data directory", "warning")
                if show_message:
                    QMessageBox.warning(
                        self.parent,
                        "No Data Files",
                        f"No CSV files were found in the '{self.data_dir}' directory."
                    )
                return False
            
            # Confirm before syncing to cloud
            if show_message:
                reply = QMessageBox.question(
                    self.parent,
                    "Confirm Upload",
                    f"This will upload {len(csv_files)} data files to the cloud. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    self.log_message("Upload cancelled by user", "warning")
                    return False
            
            # Get user ID from user_info
            user_id = 'anonymous'
            if hasattr(self, 'user_info') and self.user_info:
                if 'localId' in self.user_info:
                    user_id = self.user_info['localId']
                elif 'userId' in self.user_info:
                    user_id = self.user_info['userId']
                elif 'uid' in self.user_info:
                    user_id = self.user_info['uid']
                elif 'email' in self.user_info:
                    # Use email as fallback ID
                    user_id = self.user_info['email'].replace('@', '_at_').replace('.', '_dot_')
            
            self.log_message(f"Using user ID: {user_id} for sync")
            self.log_message(f"Syncing data from directory: {self.data_dir}")
            success = firebase_integration.sync_data_to_firebase(user_id, self.data_dir)
            
            if success:
                self.log_message("Data successfully synced to cloud", "success")
                if show_message:
                    QMessageBox.information(
                        self.parent,
                        "Sync Successful",
                        "All data has been successfully uploaded to Firebase cloud storage."
                    )
                return True
            else:
                self.log_message("Failed to sync data to cloud", "error")
                if show_message:
                    QMessageBox.critical(
                        self.parent,
                        "Sync Error",
                        "An error occurred while syncing to Firebase."
                    )
                return False
        except Exception as e:
            self.log_message(f"Error in sync_to_cloud: {str(e)}", "error")
            if show_message:
                QMessageBox.critical(
                    self.parent,
                    "Sync Error",
                    f"An error occurred while syncing to Firebase: {str(e)}"
                )
            return False
    
    def sync_from_cloud(self, show_message=True):
        """
        Sync data from Firebase cloud storage.
        
        Args:
            show_message: Whether to show success/error messages
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        if not FIREBASE_AVAILABLE:
            self.log_message("Firebase integration is not available", "error")
            if show_message:
                QMessageBox.warning(
                    self.parent,
                    "Firebase Not Available",
                    "Firebase integration is not available. Please run setup_firebase.py first."
                )
            return False
        
        try:
            self.log_message("Starting sync from cloud operation...")
            self.log_message(f"Data directory: {self.data_dir}")
            
            # Initialize Firebase if not already initialized
            if not firebase_integration.initialize_firebase():
                self.log_message("Failed to initialize Firebase", "error")
                if show_message:
                    QMessageBox.warning(
                        self.parent,
                        "Firebase Error",
                        "Failed to initialize Firebase. Please check your credentials."
                    )
                return False
                
            # If not authenticated, show login dialog
            if not self.is_authenticated():
                self.log_message("User not authenticated, authentication required", "warning")
                if show_message:
                    reply = QMessageBox.question(
                        self.parent,
                        "Authentication Required",
                        "You need to sign in to download data from the cloud. Would you like to sign in now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        self.log_message("User agreed to authenticate")
                        if not self.show_login_dialog():
                            self.log_message("Login failed or cancelled by user", "warning")
                            return False
                    else:
                        self.log_message("Authentication declined by user", "warning")
                        return False
                else:
                    self.log_message("Cannot sync without authentication", "error")
                    return False
            
            # Confirm before syncing from cloud (will overwrite local data)
            if show_message:
                reply = QMessageBox.question(
                    self.parent,
                    "Confirm Download",
                    "This will download data from the cloud and overwrite your local data. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    self.log_message("Download cancelled by user", "warning")
                    return False
            
            # Create data directory if it doesn't exist
            if not os.path.exists(self.data_dir):
                self.log_message(f"Creating data directory: {self.data_dir}")
                os.makedirs(self.data_dir)
                
            # Get user ID from user_info
            user_id = 'anonymous'
            if hasattr(self, 'user_info') and self.user_info:
                if 'localId' in self.user_info:
                    user_id = self.user_info['localId']
                elif 'userId' in self.user_info:
                    user_id = self.user_info['userId']
                elif 'uid' in self.user_info:
                    user_id = self.user_info['uid']
                elif 'email' in self.user_info:
                    # Use email as fallback ID
                    user_id = self.user_info['email'].replace('@', '_at_').replace('.', '_dot_')
            
            self.log_message(f"Using user ID: {user_id} for sync")
            success = firebase_integration.sync_data_from_firebase(user_id, self.data_dir)
            
            if success:
                self.log_message("Data successfully downloaded from cloud", "success")
                if show_message:
                    QMessageBox.information(
                        self.parent,
                        "Download Successful",
                        "All data has been successfully downloaded from Firebase cloud storage."
                    )
                return True
            else:
                self.log_message("Failed to download data from cloud", "error")
                if show_message:
                    QMessageBox.critical(
                        self.parent,
                        "Download Error",
                        "An error occurred while downloading from Firebase."
                    )
                return False
        except Exception as e:
            self.log_message(f"Error in sync_from_cloud: {str(e)}", "error")
            if show_message:
                QMessageBox.critical(
                    self.parent,
                    "Sync Error",
                    f"An error occurred while syncing from Firebase: {str(e)}"
                )
            return False
    
    def add_sync_ui(self, parent_layout):
        """
        Add Firebase sync UI elements to the parent layout
        
        Args:
            parent_layout: The layout to add the sync UI elements to
        """
        # Create a container for the sync buttons
        sync_layout = QHBoxLayout()
        
        # Add sync to cloud button
        self.sync_to_cloud_btn = QPushButton("Sync to Cloud")
        self.sync_to_cloud_btn.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px; border-radius: 4px;"
        )
        self.sync_to_cloud_btn.clicked.connect(self.sync_to_cloud)
        sync_layout.addWidget(self.sync_to_cloud_btn)
        
        # Add sync from cloud button
        self.sync_from_cloud_btn = QPushButton("Sync from Cloud")
        self.sync_from_cloud_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 8px; border-radius: 4px;"
        )
        self.sync_from_cloud_btn.clicked.connect(self.sync_from_cloud)
        sync_layout.addWidget(self.sync_from_cloud_btn)
        
        # Add the sync layout to the parent layout
        parent_layout.addLayout(sync_layout)
        
        # Add a status label
        self.sync_status_label = QLabel("Ready to sync")
        self.sync_status_label.setAlignment(Qt.AlignCenter)
        self.sync_status_label.setStyleSheet("color: #555; margin-top: 8px;")
        parent_layout.addWidget(self.sync_status_label)
        
        # Check if Firebase is available and update UI accordingly
        if not self.is_firebase_available():
            self.sync_to_cloud_btn.setEnabled(False)
            self.sync_from_cloud_btn.setEnabled(False)
            self.sync_status_label.setText("Firebase not available")
            self.sync_status_label.setStyleSheet("color: #e74c3c; margin-top: 8px;")
        elif not self.is_authenticated():
            self.sync_to_cloud_btn.setEnabled(False)
            self.sync_from_cloud_btn.setEnabled(False)
            self.sync_status_label.setText("Not authenticated")
            self.sync_status_label.setStyleSheet("color: #f39c12; margin-top: 8px;")
        else:
            self.sync_status_label.setText(f"Authenticated as: {getattr(self, 'user_info', {}).get('email', 'unknown')}")
            self.sync_status_label.setStyleSheet("color: #27ae60; margin-top: 8px;")
