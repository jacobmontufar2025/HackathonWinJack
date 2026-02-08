import os
import json
import base64
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
else:
    model = None
    print("❌ Google API key not configured. Gemini features disabled.")

def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Candidate-Evaluator"
    }
    # Only add Authorization header if we have a valid token
    if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("ghp_"):  # Check it's not the demo token
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    elif GITHUB_TOKEN:
        print("⚠️ Using GitHub token (rate limit: 5000 requests/hour)")
    else:
        print("⚠️ No GitHub token (rate limit: 60 requests/hour)")
    return headers

def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Candidate-Evaluator"
    }
    if GITHUB_TOKEN and "PASTE_" not in GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def get_file_content(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        if "content" in data:
            try:
                return base64.b64decode(data["content"]).decode("utf-8")
            except Exception:
                return ""
    return None

def get_user_profile(username):
    print(f"👤 Fetching profile for: {username}...")
    url = f"https://api.github.com/users/{username}"
    res = requests.get(url, headers=get_headers())
    
    if res.status_code != 200:
        print(f"❌ User not found. API Status: {res.status_code}")
        return None
        
    data = res.json()
    return {
        "username": data.get("login"),
        "name": data.get("name") or data.get("login"),
        "bio": data.get("bio") or "No bio",
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers")
    }

def get_top_repos(username, limit=3):
    print(f"📚 Scanning repositories for {username}...")
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    res = requests.get(url, headers=get_headers())
    
    if res.status_code != 200:
        return []

    repos = res.json()
    if not repos:
        return []

    valid_repos = []
    # DIAGNOSTIC: Allow forks so we don't miss your work
    for r in repos:
        valid_repos.append(r)

    # Sort by Stars first, then Updated date
    valid_repos.sort(key=lambda x: (x.get("stargazers_count", 0), x.get("updated_at", "")), reverse=True)
    
    return valid_repos[:limit]

def get_repo_languages(username, repo_name):
    """Fetches the official language breakdown from GitHub."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        return res.json()  # Returns dict like {'Java': 20000, 'HTML': 500}
    return {}

def scan_repo_content(username, repo_name):
    print(f"   -> Deep scanning project: {repo_name}...")
    
    # 1. Get Metadata & Default Branch (Crucial Fix)
    meta_url = f"https://api.github.com/repos/{username}/{repo_name}"
    meta_res = requests.get(meta_url, headers=get_headers())
    
    default_branch = "main" # Fallback
    is_fork = False
    
    if meta_res.status_code == 200:
        data = meta_res.json()
        default_branch = data.get("default_branch", "main")
        is_fork = data.get("fork", False)

    # 2. Get Official Language Stats
    lang_stats = get_repo_languages(username, repo_name)
    primary_langs = ", ".join(lang_stats.keys()) if lang_stats else "Unknown"

    # 3. Get README
    readme = get_file_content(username, repo_name, "README.md") or "No README"
    
    # 4. Find Code Files using the CORRECT branch
    tree_url = f"https://api.github.com/repos/{username}/{repo_name}/git/trees/{default_branch}?recursive=1"
    tree_res = requests.get(tree_url, headers=get_headers())
    
    code_samples = ""
    found_extensions = []
    
    if tree_res.status_code == 200:
        tree = tree_res.json().get("tree", [])
        
        # Extended list of interesting extensions
        exts = (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs", 
                ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".sql", ".vue", ".dart")
        
        # Filter for code files, ignoring tests and node_modules
        files = [f for f in tree if f["path"].endswith(exts) 
                 and "test" not in f["path"].lower() 
                 and "node_modules" not in f["path"]]
        
        # SORTING FIX: Prioritize files that are NOT in the root (usually deeper = more logic)
        # and prioritize files matching the top language found in lang_stats
        files.sort(key=lambda x: len(x["path"].split('/')), reverse=True)

        # Scan up to 4 files (increased from 2)
        for file_obj in files[:4]:
            ext = os.path.splitext(file_obj["path"])[1]
            if ext not in found_extensions:
                found_extensions.append(ext)
            
            content = get_file_content(username, repo_name, file_obj["path"])
            if content:
                code_samples += f"\n--- FILE: {file_obj['path']} ---\n{content[:2000]}\n"
                
    return f"""
    REPO: {repo_name} {"(FORKED PROJECT)" if is_fork else "(ORIGINAL)"}
    DETECTED LANGUAGES (API): {primary_langs}
    FILE EXTENSIONS FOUND: {', '.join(found_extensions)}
    README: {readme[:1500]}
    CODE SAMPLES:
    {code_samples}
    ====================
    """

def analyze_candidate(profile, repos_context):
    print("\n🧠 Synthesizing Hiring Report with Gemini...")
    
    # Check if model is available
    if not model:
        print("❌ Gemini model not available. Returning mock data.")
        return {
            "candidate_name": profile.get('name') or profile.get('username'),
            "technical_score": 75,
            "estimated_level": "Mid",
            "primary_languages": ["Python", "JavaScript"],
            "technical_strengths": ["Code structure", "Documentation"],
            "red_flags": ["None"],
            "hiring_verdict": "Lean Hire",
            "summary_report": "Analysis limited due to missing API configuration."
        }
    
    prompt = f"""
    You are a Senior Technical Recruiter. Evaluate this GitHub Candidate.
    
    CANDIDATE PROFILE:
    {json.dumps(profile)}
    
    TOP PROJECT ANALYSIS:
    {repos_context}
    
    TASK:
    1. Score the candidate from 0-100 based on code quality, complexity, and stack.
    2. Identify specific languages from file extensions.
    3. Determine seniority.

    OUTPUT JSON ONLY (No Markdown):
    {{
        "candidate_name": "{profile.get('name') or profile.get('username')}",
        "technical_score": (0-100),
        "estimated_level": "Junior | Mid | Senior",
        "primary_languages": ["List specific languages found"],
        "technical_strengths": ["list"],
        "red_flags": ["list (or 'None')"],
        "hiring_verdict": "Strong Hire | Lean Hire | Pass",
        "summary_report": "2-3 sentences justifying the decision."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "```" in text:
            text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ JSON Parsing failed. Raw output:\n{response.text if 'response' in locals() else 'No response'}")
        return {"error": str(e)}

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("\n--- 🕵️‍♀️ GITHUB CANDIDATE SCORER ---")
    username = input("Enter GitHub Username: ").strip()
    
    if username:
        profile = get_user_profile(username)
        if profile:
            top_repos = get_top_repos(username, limit=3)
            
            if not top_repos:
                print("❌ No accessible repositories found.")
            else:
                full_context = ""
                for repo in top_repos:
                    full_context += scan_repo_content(username, repo['name'])
                
                report = analyze_candidate(profile, full_context)
                
                # Visual Output
                score = report.get('technical_score', 0)
                stars = "⭐" * (int(score) // 20)
                
                print("\n" + "="*50)
                print(f"📄 HIRING REPORT: {username.upper()}")
                print(f"🏆 SCORE: {score}/100 {stars}")
                print("="*50)
                print(json.dumps(report, indent=4))