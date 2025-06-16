@echo off
echo ========================================
echo Enable Firebase for v1.1.1
echo ========================================
echo.

REM Check Python version
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Using Python 3.12
    set PYTHON_CMD=py -3.12
) else (
    python --version | findstr "3.13" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✓ Using Python 3.13
        set PYTHON_CMD=python
    ) else (
        echo ❌ ERROR: Python 3.12 or 3.13 required!
        pause
        exit /b 1
    )
)

echo.
echo Step 1: Updating pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Step 2: Installing compatible urllib3 (fixes urllib3.contrib.appengine error)...
%PYTHON_CMD% -m pip install "urllib3<2.0" --force-reinstall
%PYTHON_CMD% -m pip install "requests>=2.25.0,<3.0" --force-reinstall

echo.
echo Step 3: Installing Firebase Admin SDK...
%PYTHON_CMD% -m pip install --upgrade firebase-admin>=6.0.0
if %errorlevel% neq 0 (
    echo ⚠️ Firebase Admin installation failed
)

echo.
echo Step 4: Installing Pyrebase4...
%PYTHON_CMD% -m pip install --upgrade pyrebase4>=4.5.0
if %errorlevel% neq 0 (
    echo ⚠️ Pyrebase4 installation failed
)

echo.
echo Step 5: Installing Google Cloud dependencies...
%PYTHON_CMD% -m pip install --upgrade google-cloud-firestore>=2.11.0
%PYTHON_CMD% -m pip install --upgrade google-auth>=2.17.0
%PYTHON_CMD% -m pip install --upgrade google-auth-oauthlib>=1.0.0

echo.
echo Step 6: Installing authentication dependencies...
%PYTHON_CMD% -m pip install --upgrade PyJWT>=2.8.0
%PYTHON_CMD% -m pip install --upgrade cryptography>=41.0.0
%PYTHON_CMD% -m pip install --upgrade python-dotenv>=1.0.0

echo.
echo Step 7: Installing utility dependencies...
%PYTHON_CMD% -m pip install --upgrade requests>=2.28.0
%PYTHON_CMD% -m pip install --upgrade urllib3>=1.26.0
%PYTHON_CMD% -m pip install --upgrade certifi>=2022.12.7
%PYTHON_CMD% -m pip install --upgrade json5>=0.9.10

echo.
echo Step 8: Running Firebase enablement script...
%PYTHON_CMD% enable_firebase_v1.1.1.py

echo.
echo Step 9: Verifying Firebase imports...
%PYTHON_CMD% -c "import firebase_admin; print('✓ Firebase Admin SDK')"
if %errorlevel% neq 0 (
    echo ❌ Firebase Admin import failed
    goto :error
)

%PYTHON_CMD% -c "import pyrebase; print('✓ Pyrebase4')"
if %errorlevel% neq 0 (
    echo ❌ Pyrebase4 import failed
    goto :error
)

%PYTHON_CMD% -c "import google.cloud.firestore; print('✓ Google Cloud Firestore')"
if %errorlevel% neq 0 (
    echo ❌ Google Cloud Firestore import failed
    goto :error
)

%PYTHON_CMD% -c "import jwt; print('✓ PyJWT')"
if %errorlevel% neq 0 (
    echo ❌ PyJWT import failed
    goto :error
)

echo.
echo ========================================
echo ✅ FIREBASE SUCCESSFULLY ENABLED!
echo ========================================
echo.
echo Firebase features now available:
echo ✓ Firebase Authentication
echo ✓ Cloud Firestore Database
echo ✓ Real-time Sync
echo ✓ Multi-user Support
echo ✓ Subscription-based Access
echo.
echo Configuration files created:
echo - firebase_config.json (update with your Firebase project)
echo - .env (update with your Firebase credentials)
echo.
echo Next steps:
echo 1. Set up your Firebase project at https://console.firebase.google.com
echo 2. Update firebase_config.json with your project details
echo 3. Update .env file with your Firebase credentials
echo 4. Run: build_release_v1.1.1.bat
echo.
goto :end

:error
echo.
echo ========================================
echo ❌ FIREBASE ENABLEMENT FAILED
echo ========================================
echo.
echo Some Firebase dependencies failed to install.
echo.
echo Troubleshooting:
echo 1. Check your internet connection
echo 2. Try: pip install --upgrade pip setuptools wheel
echo 3. Try: pip install firebase-admin pyrebase4 --no-cache-dir
echo 4. Check Python version compatibility
echo.

:end
pause
