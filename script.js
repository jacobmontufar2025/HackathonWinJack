// DOM Elements
const usernameInput = document.getElementById('githubUsername');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const retryBtn = document.getElementById('retryBtn');
const exportBtn = document.getElementById('exportBtn');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const exampleTags = document.querySelectorAll('.example-tag');

// Result elements
const profileAvatar = document.getElementById('profileAvatar');
const profileName = document.getElementById('profileName');
const profileBio = document.getElementById('profileBio');
const repoCount = document.getElementById('repoCount');
const followerCount = document.getElementById('followerCount');
const scoreValue = document.getElementById('scoreValue');
const circleProgress = document.getElementById('circleProgress');
const scoreStars = document.getElementById('scoreStars');
const scoreVerdict = document.getElementById('scoreVerdict');
const seniorityLevel = document.getElementById('seniorityLevel');
const languagesList = document.getElementById('languagesList');
const strengthsList = document.getElementById('strengthsList');
const redFlagsList = document.getElementById('redFlagsList');
const summaryReport = document.getElementById('summaryReport');

// Progress steps
const progressSteps = document.querySelectorAll('.progress-steps .step');
let currentReport = null;

// Event Listeners
analyzeBtn.addEventListener('click', analyzeCandidate);
retryBtn.addEventListener('click', () => {
    errorSection.style.display = 'none';
    usernameInput.focus();
});
exportBtn.addEventListener('click', exportReport);
analyzeAnotherBtn.addEventListener('click', resetForm);

// Example tags
exampleTags.forEach(tag => {
    tag.addEventListener('click', () => {
        usernameInput.value = tag.dataset.username;
        analyzeCandidate();
    });
});

// Enter key support
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        analyzeCandidate();
    }
});

async function analyzeCandidate() {
    const username = usernameInput.value.trim();
    
    if (!username) {
        showError('Please enter a GitHub username');
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Step 1: Fetch Profile
        updateProgress(1);
        const profile = await fetchFromBackend('/analyze', { username });
        
        if (!profile || profile.error) {
            throw new Error(profile?.error || 'Failed to fetch profile');
        }
        
        // Update UI with profile data
        updateProfileUI(profile);
        
        // Step 2: Fetch Report
        updateProgress(4);
        const report = await fetchFromBackend('/generate-report', { username });
        
        if (!report || report.error) {
            throw new Error(report?.error || 'Failed to generate report');
        }
        
        currentReport = report;
        
        // Update UI with report data
        updateReportUI(report);
        
        // Show results
        showResults();
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError(error.message || 'Failed to analyze candidate. Please check the username and try again.');
    }
}

// Remove the simulateBackendResponse function entirely and use this:
async function fetchFromBackend(endpoint, data) {
    // Local development
    const API_BASE_URL = 'http://localhost:5000/api';
    
    // For production deployment, you would use:
    // const API_BASE_URL = 'https://your-python-backend.herokuapp.com/api';
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

// Update the analyzeCandidate function endpoints:
async function analyzeCandidate() {
    const username = usernameInput.value.trim();
    
    if (!username) {
        showError('Please enter a GitHub username');
        return;
    }
    
    showLoading();
    
    try {
        // Step 1: Fetch Profile
        updateProgress(1);
        const profile = await fetchFromBackend('/analyze-profile', { username });
        
        // Add avatar URL to profile
        profile.avatar_url = `https://github.com/${username}.png`;
        
        updateProfileUI(profile);
        
        // Steps 2-3: Simulated scanning
        updateProgress(2);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateProgress(3);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Step 4: Generate Report
        updateProgress(4);
        const report = await fetchFromBackend('/generate-report', { username });
        
        currentReport = report;
        updateReportUI(report);
        showResults();
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showError(error.message || 'Failed to analyze candidate. Please check the username and try again.');
    }
}

function updateProgress(step) {
    progressSteps.forEach((stepElement, index) => {
        if (index < step) {
            stepElement.classList.add('active');
        } else {
            stepElement.classList.remove('active');
        }
    });
}

function updateProfileUI(profile) {
    profileAvatar.src = profile.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.name)}&size=120`;
    profileName.textContent = profile.name;
    profileBio.textContent = profile.bio;
    repoCount.textContent = profile.public_repos;
    followerCount.textContent = profile.followers;
}

function updateReportUI(report) {
    // Update score
    scoreValue.textContent = report.technical_score;
    const percentage = report.technical_score;
    circleProgress.style.background = `conic-gradient(var(--accent) 0% ${percentage}%, var(--gray) ${percentage}% 100%)`;
    
    // Update stars
    const starCount = Math.floor(report.technical_score / 20);
    scoreStars.innerHTML = '⭐'.repeat(starCount);
    
    // Update verdict
    scoreVerdict.textContent = report.hiring_verdict;
    if (report.hiring_verdict === 'Strong Hire') {
        scoreVerdict.style.background = 'rgba(0, 184, 148, 0.1)';
        scoreVerdict.style.color = 'var(--success)';
    } else if (report.hiring_verdict === 'Lean Hire') {
        scoreVerdict.style.background = 'rgba(253, 203, 110, 0.1)';
        scoreVerdict.style.color = 'var(--warning)';
    } else {
        scoreVerdict.style.background = 'rgba(225, 112, 85, 0.1)';
        scoreVerdict.style.color = 'var(--danger)';
    }
    
    // Update seniority
    seniorityLevel.textContent = report.estimated_level;
    
    // Update languages
    languagesList.innerHTML = '';
    report.primary_languages.forEach(lang => {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = lang;
        languagesList.appendChild(tag);
    });
    
    // Update strengths
    strengthsList.innerHTML = '';
    report.technical_strengths.forEach(strength => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fas fa-check-circle"></i> ${strength}`;
        strengthsList.appendChild(li);
    });
    
    // Update red flags
    redFlagsList.innerHTML = '';
    report.red_flags.forEach(flag => {
        const li = document.createElement('li');
        if (flag === 'None') {
            li.innerHTML = `<i class="fas fa-check-circle"></i> No significant red flags detected`;
            li.style.color = 'var(--success)';
        } else {
            li.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${flag}`;
            li.style.color = 'var(--danger)';
        }
        redFlagsList.appendChild(li);
    });
    
    // Update summary
    summaryReport.textContent = report.summary_report;
}

function showLoading() {
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'block';
}

function showResults() {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    loadingSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function exportReport() {
    // 1. Check if there is a report to save
    if (!currentReport) return;

    // 2. Create a formatted text string
    let textContent = `GITHUB CANDIDATE REPORT\n`;
    textContent += `=======================\n\n`;
    textContent += `Candidate: ${currentReport.candidate_name}\n`;
    textContent += `Score:     ${currentReport.technical_score}/100\n`;
    textContent += `Level:     ${currentReport.estimated_level}\n`;
    textContent += `Verdict:   ${currentReport.hiring_verdict}\n\n`;

    textContent += `-----------------------\n`;
    textContent += `PRIMARY LANGUAGES\n`;
    textContent += `-----------------------\n`;
    // Join the array items with a newline and a dash
    textContent += `- ${currentReport.primary_languages.join('\n- ')}\n\n`;

    textContent += `-----------------------\n`;
    textContent += `TECHNICAL STRENGTHS\n`;
    textContent += `-----------------------\n`;
    textContent += `- ${currentReport.technical_strengths.join('\n- ')}\n\n`;

    textContent += `-----------------------\n`;
    textContent += `RED FLAGS\n`;
    textContent += `-----------------------\n`;
    textContent += `- ${currentReport.red_flags.join('\n- ')}\n\n`;

    textContent += `-----------------------\n`;
    textContent += `SUMMARY\n`;
    textContent += `-----------------------\n`;
    textContent += `${currentReport.summary_report}\n`;

    // 3. Create a Blob (file object) with "text/plain" type
    const blob = new Blob([textContent], { type: 'text/plain' });
    
    // 4. Create a temporary URL for the file
    const url = URL.createObjectURL(blob);

    // 5. Create a download link and click it programmatically
    const a = document.createElement('a');
    a.href = url;
    a.download = `github-report-${usernameInput.value}.txt`; // .txt extension
    document.body.appendChild(a);
    a.click();
    
    // 6. Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function resetForm() {
    usernameInput.value = '';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    usernameInput.focus();
}

// DVD Logo Animation - Add this to your script.js file
function createDvdLogo() {
    const dvdLogo = document.createElement('div');
    dvdLogo.className = 'dvd-logo';
    document.body.appendChild(dvdLogo);
    
    // Adjust these based on your PNG dimensions
    const logoWidth = 120;  // Your PNG width
    const logoHeight = 60;  // Your PNG height
    
    let x = Math.random() * (window.innerWidth - logoWidth);
    let y = Math.random() * (window.innerHeight - logoHeight);
    let xSpeed = 2;
    let ySpeed = 2;
    
    // Update logo position
    function updatePosition() {
        x += xSpeed;
        y += ySpeed;
        
        // Bounce off walls
        if (x + logoWidth >= window.innerWidth || x <= 0) {
            xSpeed = -xSpeed;
        }
        
        if (y + logoHeight >= window.innerHeight || y <= 0) {
            ySpeed = -ySpeed;
        }
        
        // Apply position
        dvdLogo.style.left = `${x}px`;
        dvdLogo.style.top = `${y}px`;
        
        // Continue animation
        requestAnimationFrame(updatePosition);
    }
    
    // Start animation
    updatePosition();
    
    // Pause on hover
    dvdLogo.addEventListener('mouseenter', () => {
        const tempXSpeed = xSpeed;
        const tempYSpeed = ySpeed;
        xSpeed = 0;
        ySpeed = 0;
        
        dvdLogo.addEventListener('mouseleave', () => {
            xSpeed = tempXSpeed;
            ySpeed = tempYSpeed;
        }, { once: true });
    });
    
    // Make it draggable for fun
    let isDragging = false;
    let dragOffsetX, dragOffsetY;
    
    dvdLogo.style.pointerEvents = 'auto';
    
    dvdLogo.addEventListener('mousedown', (e) => {
        isDragging = true;
        dragOffsetX = e.clientX - x;
        dragOffsetY = e.clientY - y;
        dvdLogo.style.cursor = 'grabbing';
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        x = e.clientX - dragOffsetX;
        y = e.clientY - dragOffsetY;
        
        // Keep within bounds
        x = Math.max(0, Math.min(x, window.innerWidth - 120));
        y = Math.max(0, Math.min(y, window.innerHeight - 60));
        
        dvdLogo.style.left = `${x}px`;
        dvdLogo.style.top = `${y}px`;
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            dvdLogo.style.cursor = 'grab';
        }
    });
}

// Create DVD logo when page loads
window.addEventListener('load', createDvdLogo);

// Backend Integration Instructions
console.log(`
GitHub Candidate Scorer Frontend

To connect with your Python backend:

1. Start your Python Flask/FastAPI server:
   pip install flask flask-cors
   
   Create a server.py:
   from flask import Flask, request, jsonify
   from flask_cors import CORS
   from github_analyzer import get_user_profile, get_top_repos, scan_repo_content, analyze_candidate

   app = Flask(__name__)
   CORS(app)

   @app.route('/analyze', methods=['POST'])
   def analyze():
       data = request.json
       username = data.get('username')
       profile = get_user_profile(username)
       return jsonify(profile)

   @app.route('/generate-report', methods=['POST'])
   def generate_report():
       data = request.json
       username = data.get('username')
       profile = get_user_profile(username)
       top_repos = get_top_repos(username, limit=3)
       full_context = ""
       for repo in top_repos:
           full_context += scan_repo_content(username, repo['name'])
       report = analyze_candidate(profile, full_context)
       return jsonify(report)

   if __name__ == '__main__':
       app.run(debug=True, port=5000)

2. Update script.js fetchFromBackend() function:
   async function fetchFromBackend(endpoint, data) {
       const response = await fetch('http://localhost:5000' + endpoint, {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
           },
           body: JSON.stringify(data)
       });
       return await response.json();
   }
`);