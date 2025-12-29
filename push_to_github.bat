@echo off
echo ==========================================
echo       Push Eco-Sync to GitHub
echo ==========================================
echo.
echo 1. Go to https://github.com/new
echo 2. Create a repository named "ECOSync"
echo 3. Copy the HTTPS URL (e.g., https://github.com/username/ECOSync.git)
echo.
set /p REPO_URL="Paste Repository URL here: "

if "%REPO_URL%"=="" goto error

echo.
echo Adding remote origin...
git remote add origin %REPO_URL%

echo.
echo Renaming branch to main...
git branch -M main

echo.
echo Pushing code...
git push -u origin main

echo.
echo DONE!
pause
exit

:error
echo Error: URL cannot be empty.
pause
