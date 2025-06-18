# Firebase Setup Guide for Kitchen Dashboard v1.0.6 (Online-Only Mode)

This guide will help you set up Firebase authentication and cloud sync for the Kitchen Dashboard application.

**⚠️ IMPORTANT: This application requires online authentication and does not support offline mode.**

## Prerequisites

1. **Python Dependencies**: Ensure you have the required packages installed:
   ```bash
   pip install pyrebase4 firebase-admin
   ```

2. **Firebase Project**: You need a Firebase project with Authentication and Firestore enabled.

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "kitchen-dashboard")
4. Follow the setup wizard

## Step 2: Enable Authentication

1. In your Firebase project, go to **Authentication** > **Sign-in method**
2. Enable **Email/Password** authentication
3. Optionally, enable other sign-in methods as needed

## Step 3: Enable Firestore Database

1. Go to **Firestore Database**
2. Click "Create database"
3. Choose "Start in test mode" for development (you can secure it later)
4. Select a location for your database

## Step 4: Get Firebase Configuration

1. Go to **Project Settings** (gear icon)
2. Scroll down to "Your apps" section
3. Click "Add app" and select the web icon (</>)
4. Register your app with a nickname (e.g., "Kitchen Dashboard")
5. Copy the Firebase configuration object

## Step 5: Configure the Application

### Option 1: Using firebase_config.json (Recommended)

1. Open the `firebase_config.json` file in the project root
2. Replace the placeholder values with your Firebase configuration:

```json
{
  "firebase": {
    "apiKey": "your-actual-api-key",
    "authDomain": "your-project.firebaseapp.com",
    "databaseURL": "https://your-project-default-rtdb.firebaseio.com",
    "projectId": "your-actual-project-id",
    "storageBucket": "your-project.appspot.com",
    "messagingSenderId": "your-sender-id",
    "appId": "your-app-id",
    "measurementId": "your-measurement-id"
  }
}
```

### Option 2: Using Environment Variables

1. Copy `.env.template` to `.env`
2. Fill in your Firebase configuration in the `.env` file

## Step 6: Test the Setup

1. Run the Kitchen Dashboard application
2. You should see a login dialog on startup
3. Create a test user account or use an existing one
4. Verify that authentication works and data syncs to Firebase

## Security Rules (Important!)

For production use, update your Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Features Enabled in v1.0.6 (Online-Only Mode)

- ✅ Firebase Authentication with Email/Password (Required)
- ✅ Cloud Sync for all application data
- ✅ Real-time synchronization
- ❌ **No Offline Support** - Online connection required at all times
- ✅ User session management
- ✅ Automatic daily sync
- ✅ Manual sync controls
- ✅ Conflict resolution
- ⚠️ **Application exits if authentication fails or connection is lost**

## Troubleshooting

### Common Issues:

1. **"Firebase not configured" error**
   - Check that `firebase_config.json` has valid configuration
   - Ensure all required fields are filled

2. **Authentication fails**
   - Verify Email/Password is enabled in Firebase Console
   - Check that the email/password combination is correct
   - Ensure the user account exists in Firebase Authentication

3. **Sync not working**
   - Check Firestore rules allow read/write for authenticated users
   - Verify internet connection
   - Check application logs for detailed error messages

4. **"pyrebase4 not found" error**
   - Install the required package: `pip install pyrebase4`

### Getting Help

If you encounter issues:
1. Check the application logs in the Settings > Logs tab
2. Verify your Firebase project settings
3. Ensure all dependencies are installed
4. Check the Firebase Console for any error messages

## Advanced Configuration

You can customize the Firebase integration by modifying:
- Sync intervals in `firebase_config.json`
- Security settings for session timeout
- Conflict resolution strategies
- Batch sizes for optimal performance

The application is optimized for Firebase's free tier limits and will automatically manage read/write quotas.
