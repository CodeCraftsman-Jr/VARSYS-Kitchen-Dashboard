@echo off
echo ========================================
echo Fix urllib3 Firebase Compatibility
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
echo The issue: urllib3 2.0+ removed urllib3.contrib.appengine
echo Firebase packages still expect this module
echo.
echo Solution: Install compatible urllib3 version
echo.

echo Step 1: Installing compatible urllib3 version...
%PYTHON_CMD% -m pip install "urllib3<2.0" --force-reinstall
if %errorlevel% neq 0 (
    echo ❌ Failed to install compatible urllib3
    goto :error
)

echo.
echo Step 2: Installing compatible requests...
%PYTHON_CMD% -m pip install "requests>=2.25.0,<3.0" --force-reinstall

echo.
echo Step 3: Reinstalling Firebase packages...
%PYTHON_CMD% -m pip install firebase-admin --force-reinstall
%PYTHON_CMD% -m pip install pyrebase4 --force-reinstall

echo.
echo Step 4: Installing Google packages...
%PYTHON_CMD% -m pip install "google-auth>=2.0.0,<3.0" --force-reinstall
%PYTHON_CMD% -m pip install google-auth-httplib2 --force-reinstall
%PYTHON_CMD% -m pip install google-cloud-firestore --force-reinstall

echo.
echo Step 5: Testing Firebase imports...
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

%PYTHON_CMD% -c "import google.auth; print('✓ Google Auth')"
if %errorlevel% neq 0 (
    echo ❌ Google Auth import failed
    goto :error
)

echo.
echo Step 6: Testing urllib3.contrib.appengine...
%PYTHON_CMD% -c "import urllib3.contrib.appengine; print('✓ urllib3.contrib.appengine available')"
if %errorlevel% neq 0 (
    echo ⚠️ urllib3.contrib.appengine not available, running workaround...
    %PYTHON_CMD% fix_urllib3_firebase.py
)

echo.
echo Step 7: Final Firebase test...
%PYTHON_CMD% -c "import firebase_admin, pyrebase, google.auth; print('✅ All Firebase packages working!')"
if %errorlevel% neq 0 (
    echo ❌ Final Firebase test failed
    goto :error
)

echo.
echo ========================================
echo ✅ FIREBASE URLLIB3 FIX SUCCESSFUL!
echo ========================================
echo.
echo Firebase packages are now compatible:
echo ✓ urllib3 < 2.0 (compatible version)
echo ✓ Firebase Admin SDK working
echo ✓ Pyrebase4 working
echo ✓ Google Auth working
echo ✓ All imports successful
echo.
echo Next steps:
echo 1. Run: python test_firebase_enabled.py
echo 2. Run: build_release_v1.1.1.bat
echo 3. Test Firebase features in application
echo.
goto :end

:error
echo.
echo ========================================
echo ❌ FIREBASE URLLIB3 FIX FAILED
echo ========================================
echo.
echo Manual fix steps:
echo 1. pip uninstall urllib3 requests firebase-admin pyrebase4
echo 2. pip install "urllib3==1.26.18"
echo 3. pip install "requests==2.31.0"
echo 4. pip install firebase-admin pyrebase4
echo 5. Test: python -c "import firebase_admin, pyrebase"
echo.

:end
pause
