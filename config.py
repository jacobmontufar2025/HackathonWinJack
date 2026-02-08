# config.py
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class KeyRotationManager:
    def __init__(self, config_file: str = "keys_config.json"):
        self.config_file = config_file
        self.keys = self.load_keys()
        
    def load_keys(self) -> Dict:
        """Load key configuration from file or environment"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.create_default_config()
        return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default configuration with environment variables"""
        return {
            "github_tokens": [
                {
                    "token": os.getenv("GITHUB_TOKEN", ""),
                    "last_used": None,
                    "rate_limit_remaining": 5000,
                    "rate_limit_reset": None,
                    "active": True,
                    "name": "primary_token"
                }
            ],
            "google_api_keys": [
                {
                    "key": os.getenv("GOOGLE_API_KEY", ""),
                    "last_used": None,
                    "quota_remaining": 1000,
                    "active": True,
                    "name": "primary_key"
                }
            ],
            "rotation_strategy": {
                "github": "round_robin",
                "google": "round_robin",
                "retry_on_quota": True,
                "fallback_enabled": True
            },
            "github_rate_limit_threshold": 100,
            "google_quota_threshold": 50
        }
    
    def save_keys(self):
        """Save current key configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def get_github_token(self) -> Optional[str]:
        """Get next available GitHub token using rotation strategy"""
        strategy = self.keys["rotation_strategy"]["github"]
        
        if strategy == "round_robin":
            # Get active tokens
            active_tokens = [t for t in self.keys["github_tokens"] 
                           if t.get("active", True)]
            
            if not active_tokens:
                return None
            
            # Sort by last used (oldest first)
            active_tokens.sort(key=lambda x: datetime.fromisoformat(x.get("last_used")) if x.get("last_used") else datetime.min)
            
            token = active_tokens[0]
            token["last_used"] = datetime.now().isoformat()
            self.save_keys()
            return token["token"]
        
        elif strategy == "quota_based":
            # Get token with highest rate limit remaining
            active_tokens = [t for t in self.keys["github_tokens"] 
                           if t.get("active", True)]
            
            if not active_tokens:
                return None
            
            token = max(active_tokens, key=lambda x: x.get("rate_limit_remaining", 0))
            token["last_used"] = datetime.now().isoformat()
            self.save_keys()
            return token["token"]
        
        return None
    
    def get_google_api_key(self) -> Optional[str]:
        """Get next available Google API key"""
        strategy = self.keys["rotation_strategy"]["google"]
        
        if strategy == "round_robin":
            active_keys = [k for k in self.keys["google_api_keys"] 
                          if k.get("active", True)]
            
            if not active_keys:
                return None
            
            active_keys.sort(key=lambda x: datetime.fromisoformat(x.get("last_used")) if x.get("last_used") else datetime.min)
            
            key = active_keys[0]
            key["last_used"] = datetime.now().isoformat()
            self.save_keys()
            return key["key"]
        
        return None
    
    def update_github_rate_limit(self, token: str, remaining: int, reset_time: int):
        """Update rate limit information for a GitHub token"""
        for t in self.keys["github_tokens"]:
            if t["token"] == token:
                t["rate_limit_remaining"] = remaining
                t["rate_limit_reset"] = reset_time
                
                # Auto-deactivate if below threshold
                if remaining < self.keys["github_rate_limit_threshold"]:
                    t["active"] = False
                    print(f"⚠️ Token {t['name']} deactivated (rate limit: {remaining})")
                
                self.save_keys()
                break
    
    def update_google_quota(self, key: str, quota_used: int):
        """Update quota usage for Google API key"""
        for k in self.keys["google_api_keys"]:
            if k["key"] == key:
                k["quota_remaining"] = max(0, 1000 - quota_used)
                
                if k["quota_remaining"] < self.keys["google_quota_threshold"]:
                    k["active"] = False
                    print(f"⚠️ Google key {k['name']} deactivated (quota low)")
                
                self.save_keys()
                break
    
    def add_github_token(self, token: str, name: str = None):
        """Add a new GitHub token to rotation"""
        self.keys["github_tokens"].append({
            "token": token,
            "last_used": None,
            "rate_limit_remaining": 5000,
            "rate_limit_reset": None,
            "active": True,
            "name": name or f"token_{len(self.keys['github_tokens'])}"
        })
        self.save_keys()
    
    def add_google_key(self, key: str, name: str = None):
        """Add a new Google API key to rotation"""
        self.keys["google_api_keys"].append({
            "key": key,
            "last_used": None,
            "quota_remaining": 1000,
            "active": True,
            "name": name or f"google_key_{len(self.keys['google_api_keys'])}"
        })
        self.save_keys()

# Create singleton instance
key_manager = KeyRotationManager()