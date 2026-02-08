# HackathonWinJack: AI-Powered GitHub Repository Analyzer
HackathonWinJack is a web application that analyzes GitHub repositories using AI to extract key insights, statistics, and project summaries. Perfect for hackathon judges, project evaluators, and developers who want to quickly understand repository quality and content.

# Features
* Repository Analysis: Extracts critical information from any public GitHub repository
* AI-Powered Summaries: Generates intelligent insights using Claude AI (Anthropic API)
* Interactive Dashboard: Clean web interface with real-time analysis results
* Export Functionality: Export analysis results for documentation

# Technology Stack
| Component | Technology |
| --- | --- |
| Backend	| Python (Flask) |
| Frontend	| HTML, CSS, JavaScript |
| AI Integration	| Anthropic Claude API |
| Version Control	| Git/GitHub |
| Other	| GitHub API |

# Project Structure
```
HackathonWinJack/
├── server.py              # Main Flask application
├── github_analyzer.py     # GitHub API integration and analysis logic
├── config.py             # Configuration and API key management
├── requirements.txt      # Python dependencies
├── index.html           # Main web interface
├── style.css            # Styling
├── script.js            # Frontend functionality
├── dvd-logo.png         # Bouncing logo asset
└── .gitignore          # Git ignore rules
```

# Getting Started
## Prerequisites
* Python 3.7+
* GitHub account (for repository access)
* Anthropic API key (for AI analysis features)

## Installation
### 1. Clone the Repository
```
git clone https://github.com/username/repository.git
cd repository
```

### 2. Install dependencies
```
pip install -r requirements.txt
```
### 3. Configure API keys

* Copy config.py.example to config.py (if exists)
* Add your Anthropic API key to config.py
* Note: The project has multiple API key support for team collaboration

### 4. Run the application
```
python server.py
```
### 5. Open in browser
Navigate to `http://localhost:5000`

# How to Use
1. **Enter Repository URL:** Input any public GitHub repository URL
2. **Analyze:** Click the analyze button to fetch repository data
3. **View Insights:** See AI-generated summary, statistics, and key metrics
4. **Export:** Download results as HTML for reporting

# Configuration
The application requires the following configurations:
- **GitHub API**: No token needed for public repositories (rate limits apply)
- **Anthropic API**: Required for AI analysis features
- **Server Settings**: Configured in `server.py` for local development

# Contributors
- **Anthony Vallejo**: Added multiple API key support and configuration updates
- **Jacob Montufar**: Project initialization and core functionality

# Notes & Limitations
- **API Rate Limits**: GitHub API has rate limits for unauthenticated requests
- **AI Costs**: Anthropic API usage may incur costs depending on usage volume
- **Repository Scope**: Currently optimized for analyzing single repositories
- **Development Status**: Actively developed with recent updates on February 8, 2026

# License
This project is currently without an explicit license. Please contact the repository owner for usage permissions.

# Acknowledgements
- **GitHub API** for repository data access
- **Anthropic** for Claude AI capabilities
- **All Contributors** who have helped shape this project

---

**Last Updated**: February 8, 2026
**Project Status**: Active Development
**Primary Language**: Python (42.8%) with JavaScript, CSS, and HTML components

For questions or support, please open an issue in the GitHub repository.
