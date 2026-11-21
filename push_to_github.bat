@echo off
echo === KnightScope GitHub Push Script ===
echo.
echo This will push the HTML/CSS/JS website to GitHub.
echo.
cd /d "c:\Users\chait\Documents\Knight Scope"
git config --global --add safe.directory "C:/Users/chait/Documents/Knight Scope"
git config user.email "knightscope@deepknights.ai"
git config user.name "Deep Knights"
git add index.html serve.py render.yaml requirements.txt
git status
echo.
echo Run the following to commit and push:
echo   git commit -m "Rebuild: Full HTML/CSS/JS application with all 4 AI algorithms"
echo   git push origin main
pause
