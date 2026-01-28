# ApplyTailored - AI-Powered Resume Tailoring System

An intelligent job application management system that uses Claude AI to automatically tailor resumes to job descriptions.

## Features

- 🤖 **AI-Powered Resume Tailoring**: Uses Claude Sonnet 4 to analyze job descriptions and customize your resume
- 📄 **LaTeX Resume Generation**: Compiles professional PDFs from LaTeX templates
- 💼 **Job Application Tracking**: Manage all your job applications in one place
- 📊 **Job Analysis**: Automatically extracts key information from job descriptions
- ✉️ **Cover Letter Generation**: AI-generated cover letters tailored to each position
- 👤 **User Authentication**: Secure JWT-based authentication system
- 📁 **Document Management**: Store and download generated resumes and cover letters

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: Anthropic Claude API
- **Document Processing**: LaTeX (pdflatex)
- **Authentication**: JWT
- **Frontend**: HTML, Tailwind CSS, Jinja2

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
2. **MongoDB** (running locally or remote)
3. **LaTeX Distribution**:
   - **Linux**: `sudo apt-get install texlive-full`
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Install MiKTeX from https://miktex.org/
4. **Anthropic API Key**: Sign up at https://console.anthropic.com/

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd applytailored
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-key-change-this
MONGO_URI=mongodb://localhost:27017
DB_NAME=applytailored
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 5. Initialize Database

Run the seeding script to set up initial data and indexes:

```bash
python seed_database.py
```

This will:
- Create necessary MongoDB indexes
- Set up the default base resume template
- Verify storage directories exist

### 6. Verify LaTeX Installation

Test if pdflatex is installed:

```bash
pdflatex --version
```

If you see version information, you're good to go!

## Project Structure

```
applytailored/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── db.py                          # Database connection
├── seed_database.py               # Database initialization script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── controllers/
│   ├── ai_controller_updated.py           # AI processing logic
│   ├── application_controller_updated.py  # Application CRUD operations
│   ├── auth_controller.py                 # Authentication logic
│   ├── dashboard_controller.py            # Dashboard logic
│   └── profile_controller.py              # Profile management
│
├── models/
│   ├── user.py                    # User model
│   ├── job_application_updated.py # Enhanced job application model
│   ├── base_resume.py             # Base resume template model
│   └── generated_asset.py         # Generated documents model
│
├── services/
│   ├── claude_ai_service.py       # Claude API integration
│   └── latex_service.py           # LaTeX compilation service
│
├── routes/
│   ├── auth_routes.py             # Authentication routes
│   ├── dashboard_routes.py        # Dashboard routes
│   ├── profile_routes.py          # Profile routes
│   └── application_routes_updated.py  # Application routes with AI features
│
├── middlewares/
│   └── auth_middleware.py         # JWT authentication middleware
│
├── views/                         # HTML templates (Jinja2)
│   ├── layouts/
│   ├── partials/
│   ├── auth/
│   ├── dashboard/
│   ├── profile/
│   └── applications/
│       ├── index.html
│       ├── modal.html
│       └── detail_updated.html    # Enhanced detail view
│
└── storage/
    ├── base_resumes/
    │   └── base_resume_template.tex  # Default resume template
    └── generated/                    # Generated PDFs and LaTeX files
```

## Usage

### 1. Start the Application

```bash
python app.py
```

The application will run on `http://localhost:5000`

### 2. Create an Account

1. Navigate to `http://localhost:5000/signup`
2. Create your account
3. Login with your credentials

### 3. Create a Job Application

1. Go to **Applications** in the sidebar
2. Click **New Application**
3. Paste the job description
4. Click **Create**

The system will automatically:
- Analyze the job description
- Extract key information (company, position, skills)
- Tailor your base resume to match the job
- Compile a professional PDF
- Store everything in your application

### 4. View Generated Documents

1. Click on any application to view details
2. See AI analysis of the job
3. Download generated PDF resume
4. Generate cover letters on demand

### 5. Customize Base Resume

To use your own resume:

1. Create a LaTeX version of your resume
2. Save it in `storage/base_resumes/`
3. Add an entry to the `base_resumes` collection in MongoDB:

```python
db.base_resumes.insert_one({
    "_id": "your-unique-id",
    "user_id": "your-user-id",
    "title": "My Professional Resume",
    "description": "My main resume template",
    "latex_template_path": "my_resume.tex",
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc)
})
```

## API Endpoints

### Authentication
- `GET /signup` - Signup page
- `POST /signup` - Create account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Applications
- `GET /applications` - List all applications
- `POST /applications` - Create new application (triggers AI processing)
- `GET /applications/<id>` - View application details
- `POST /applications/<id>/regenerate` - Regenerate resume
- `POST /applications/<id>/cover-letter` - Generate cover letter

### Assets
- `GET /assets/<id>/download` - Download generated PDF/TEX

## Database Collections

### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  password: String (hashed),
  role: String (default: "user"),
  created_at: DateTime
}
```

### applications
```javascript
{
  _id: ObjectId,
  user_id: String,
  job_description: String,
  company_name: String (optional),
  position_title: String (optional),
  status: String (draft/processing/completed/failed),
  base_resume_id: String (optional),
  generated_resume_id: String (optional),
  ai_analysis: Object (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

### base_resumes
```javascript
{
  _id: String,
  user_id: String,
  title: String,
  description: String,
  latex_template_path: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### generated_assets
```javascript
{
  _id: String,
  job_application_id: String,
  user_id: String,
  type: String (resume/cover_letter/cold_email/followup/question_answer),
  title: String,
  content_text: String,
  pdf_path: String (optional),
  tex_path: String (optional),
  ai_model: String,
  version: Integer,
  created_at: DateTime
}
```

## AI Features

### Resume Tailoring Process

1. **Job Analysis**: Claude analyzes the job description to extract:
   - Company name
   - Position title
   - Required skills
   - Preferred skills
   - Experience level
   - Key responsibilities
   - ATS keywords

2. **Resume Optimization**: Claude modifies the LaTeX resume to:
   - Emphasize relevant experience
   - Highlight matching skills
   - Reorder bullet points for relevance
   - Include ATS-optimized keywords
   - Quantify achievements where possible

3. **LaTeX Compilation**: The system compiles the tailored LaTeX to PDF

4. **Fallback Mechanism**: If compilation fails, the system uses the base resume

### Cover Letter Generation

Claude generates personalized cover letters that:
- Reference specific job requirements
- Highlight relevant achievements
- Show cultural fit
- Include clear call-to-action

## Troubleshooting

### LaTeX Compilation Errors

If you encounter LaTeX errors:

1. **Check LaTeX installation**:
   ```bash
   pdflatex --version
   ```

2. **Install missing packages**:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install texlive-latex-extra texlive-fonts-extra
   ```

3. **Check logs**: Look at `storage/generated/*.log` files

### MongoDB Connection Issues

1. **Verify MongoDB is running**:
   ```bash
   # Check if MongoDB is running
   sudo systemctl status mongod  # Linux
   brew services list            # macOS
   ```

2. **Check connection string** in `.env` file

### API Key Issues

1. Verify your Anthropic API key is valid
2. Check you have sufficient credits
3. Ensure the key has correct permissions

## Production Deployment

For production deployment:

1. **Set environment to production**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Set up async processing** with Celery for AI jobs:
   ```bash
   pip install celery redis
   ```

4. **Use environment secrets** for API keys and database credentials

5. **Set up HTTPS** for secure communication

## Future Enhancements

- [ ] Async job processing with Celery
- [ ] Multiple resume templates
- [ ] Email integration for application tracking
- [ ] Interview preparation assistant
- [ ] Application analytics dashboard
- [ ] Chrome extension for one-click applications
- [ ] LinkedIn integration
- [ ] Cover letter templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [MongoDB](https://www.mongodb.com/)
- [LaTeX](https://www.latex-project.org/)