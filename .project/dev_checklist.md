# 📋 Dev Workflow Reference (Lore AI v0)

# WHEN: Do this whenever a new tab is built, major controller logic changes,
# or after refactors. Always before committing.

# -----------------------------
# 🧪 TESTING & DEBUGGING
# -----------------------------

# Run all tests (quick pass/fail)
pytest -q

# Run smoke test only (does app launch?)
python -m unittest discover -v -s Ward_DND_AI/tests -p test_smoke.py

# Run tests and list warnings
pytest -q --tb=short -ra --disable-warnings

# Launch app GUI manually
python Ward_DND_AI/main.py

# -----------------------------
# 💾 COMMIT FLOW
# -----------------------------

# Stage all changes
git add .

# Commit with message (be specific)
git commit -m "Fix: cleaned summarize view init + added dropdown logic"

# Push to remote
git push

# -----------------------------
# ✅ CHECKPOINT CHECKLIST
# -----------------------------

# [ ] Tabs using status_var?  
# [ ] Views match controller args?  
# [ ] No unused imports or widgets?  
# [ ] Tests pass + app launches?  
# [ ] All changes committed?