# Quick Start Guide - Updating Your Existing Project

This guide will help you integrate the AI-powered resume tailoring features into your existing ApplyTailored project.

## Step-by-Step Integration

### 1. Install New Dependencies

Add to your `requirements.txt`:
```bash
anthropic==0.40.0
pydantic==2.5.3
```

Install:
```bash
pip install anthropic pydantic
```

### 2. Set Up Environment Variables

Add to your `.env` file:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key from: https://console.anthropic.com/

### 3. Add New Models

Replace/add these files in your `models/` directory:

- `models/base_resume.py` - NEW
- `models/generated_asset.py` - NEW  
- `models/job_application.py` - UPDATE with the enhanced version

### 4. Create Services Directory

Create a new `services/` directory and add:

- `services/claude_ai_service.py` - Handles all Claude API interactions
- `services/latex_service.py` - Compiles LaTeX to PDF

### 5. Update Controllers

**Replace** your existing files with the updated versions:

- `controllers/ai_controller.py` → Use `controllers/ai_controller_updated.py`
- `controllers/application_controller.py` → Use `controllers/application_controller_updated.py`

### 6. Update Routes

**Replace**:
- `routes/application_routes.py` → Use `routes/application_routes_updated.py`

This adds new endpoints:
- `/applications/<id>/regenerate` - Regenerate resume
- `/applications/<id>/cover-letter` - Generate cover letter
- `/assets/<id>/download` - Download files

### 7. Update Views

**Replace**:
- `views/applications/detail.html` → Use `views/applications/detail_updated.html`

This adds:
- AI analysis display
- Generated documents list
- Action buttons for regeneration
- Cover letter modal

### 8. Set Up Storage Directory

Create the storage structure:
```bash
mkdir -p storage/base_resumes
mkdir -p storage/generated
```

Add the base resume template:
- Copy `storage/base_resumes/base_resume_template.tex` to your project

### 9. Initialize Database

Run the seeding script to set up collections and indexes:
```bash
python seed_database.py
```

This will:
- Create database indexes for performance
- Add a default base resume entry
- Verify storage directories

### 10. Update app.py (if needed)

Make sure your `app.py` imports the updated routes:

```python
from routes.application_routes_updated import application_routes
```

### 11. Install LaTeX (if not already installed)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**macOS**:
```bash
brew install --cask mactex
```

**Windows**:
Download and install MiKTeX from: https://miktex.org/

Verify installation:
```bash
pdflatex --version
```

## File Replacement Summary

### Files to ADD (new):
```
models/base_resume.py
models/generated_asset.py
services/claude_ai_service.py
services/latex_service.py
seed_database.py
storage/base_resumes/base_resume_template.tex
```

### Files to REPLACE (updated versions):
```
controllers/ai_controller.py
controllers/application_controller.py
routes/application_routes.py
views/applications/detail.html
requirements.txt
```

### Files to KEEP (no changes needed):
```
app.py (minor import update only)
config.py
db.py
models/user.py
controllers/auth_controller.py
controllers/dashboard_controller.py
controllers/profile_controller.py
middlewares/auth_middleware.py
routes/auth_routes.py
routes/dashboard_routes.py
routes/profile_routes.py
All other views/
```

## Testing the Integration

### 1. Start MongoDB
```bash
# Linux
sudo systemctl start mongod

# macOS
brew services start mongodb-community
```

### 2. Run Database Seeding
```bash
python seed_database.py
```

Expected output:
```
✓ Verified directory: storage
✓ Verified directory: storage/base_resumes
✓ Verified directory: storage/generated
✓ Created index on users.email
✓ Created indexes on applications collection
✓ Created index on base_resumes.user_id
✓ Created indexes on generated_assets collection
✓ Created default base resume
✅ Database seeding completed successfully!
```

### 3. Start the Application
```bash
python app.py
```

### 4. Test the Flow

1. **Login/Signup**: Create an account or login
2. **Create Application**: 
   - Go to Applications
   - Click "New Application"
   - Paste a job description
   - Submit

3. **Watch AI Process**:
   - You'll be redirected to application detail
   - Status should show "processing" → "completed"
   - Generated resume will appear

4. **Test Actions**:
   - Click "Download PDF" to get tailored resume
   - Click "Generate Cover Letter" to create one
   - Click "Regenerate Resume" to create new version

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'anthropic'"
**Solution**: 
```bash
pip install anthropic
```

### Issue: "pdflatex: command not found"
**Solution**: Install LaTeX distribution (see step 11 above)

### Issue: "Application status stuck on 'processing'"
**Solution**:
1. Check logs for errors
2. Verify ANTHROPIC_API_KEY is set correctly
3. Check if LaTeX is installed properly
4. Look at MongoDB for error details in the application document

### Issue: "LaTeX compilation failed"
**Solution**:
1. Check `storage/generated/*.log` files for LaTeX errors
2. System will fallback to base resume automatically
3. Verify base resume template is valid LaTeX

### Issue: MongoDB connection error
**Solution**:
1. Ensure MongoDB is running
2. Check MONGO_URI in `.env` file
3. Verify database permissions

## Architecture Overview

```
User submits job description
         ↓
Application created in DB (status: draft)
         ↓
AI Controller processes application
         ↓
    ┌────────────────────┐
    │ Claude AI Service  │
    │ - Analyze job desc │
    │ - Tailor resume    │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  LaTeX Service     │
    │ - Compile to PDF   │
    │ - Fallback if fail │
    └────────────────────┘
         ↓
Generated Asset saved to DB
         ↓
Application status: completed
         ↓
User downloads PDF
```

## Environment Variables Checklist

Make sure your `.env` file has:

```env
✓ SECRET_KEY=...
✓ JWT_SECRET=...
✓ MONGO_URI=...
✓ DB_NAME=...
✓ ANTHROPIC_API_KEY=...  ← NEW!
```

## Next Steps After Integration

1. **Customize Base Resume**: 
   - Edit `storage/base_resumes/base_resume_template.tex`
   - Add your personal information
   - Adjust formatting to your preference

2. **Test with Real Job Postings**:
   - Copy real job descriptions
   - See how Claude tailors your resume
   - Adjust prompts if needed

3. **Monitor AI Usage**:
   - Check Anthropic console for API usage
   - Each application processes = ~2-3 API calls
   - Set up billing alerts if needed

4. **Production Considerations**:
   - Move AI processing to background jobs (Celery)
   - Add rate limiting
   - Implement caching for job analysis
   - Set up error monitoring

## Support

If you encounter issues:

1. Check the main README.md for detailed documentation
2. Review error logs in the console
3. Check MongoDB for application status and errors
4. Verify all environment variables are set

## Success Checklist

Before considering integration complete:

- [ ] All new files added
- [ ] All files updated/replaced
- [ ] Dependencies installed
- [ ] LaTeX installed and working
- [ ] MongoDB seeding completed
- [ ] Environment variables set
- [ ] Application starts without errors
- [ ] Can create account and login
- [ ] Can create new application
- [ ] Application processes with AI successfully
- [ ] Can download generated PDF
- [ ] Can generate cover letter

Congratulations! Your ApplyTailored system now has AI-powered resume tailoring! 🎉