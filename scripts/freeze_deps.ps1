# Run this with: ./scripts/freeze_deps.ps1
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: update dependencies"
git push
