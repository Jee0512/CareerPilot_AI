# Implementation Plan

## ✅ Part 1 & 2 — Already Done
- [x] Fix duplicate/ghost upload text in file uploader
- [x] Fix primary button text to #FFFFFF

## 📋 Part 3 — Enhance Continuous Learning Readiness Module

### Files to create/modify:
1. [ ] Create `modules/learning_enhancer.py` — helper functions
2. [ ] Update `app.py` — add enhanced learning section with tabs
3. [ ] Update `requirements.txt` — add `python-pptx`

### Steps:
1. [ ] Create `modules/learning_enhancer.py` with:
   - `parse_roadmap_days()` — parse existing roadmap into structured days
   - `generate_video_recommendations()` — Gemini-based video suggestions per day
   - `generate_daily_assessment()` — generate 5 MCQs per day
   - `generate_certificate_pdf()` — professional PDF certificate
   - `generate_ppt()` — PowerPoint from roadmap

2. [ ] Update `app.py`:
   - Add new session state variables
   - Replace simple roadmap display with 3-tab learning interface
   - Add assessment workflow
   - Add certificate unlock logic
   - Add progress tracking

3. [ ] Add `python-pptx` to requirements.txt

4. [ ] Test complete workflow

