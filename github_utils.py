import requests
from settings import *

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Brainsta-Admin"
}

def list_files(path):
    """List files in a GitHub repository path"""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def upload_file(path, base64_content):
    """Upload a file to GitHub repository
    
    Args:
        path: File path in repository
        base64_content: Base64 encoded file content
        
    Returns:
        dict: {"success": bool, "status": int, "message": str}
    """
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    
    try:
        # First, check if file exists and get its SHA
        get_response = requests.get(url, headers=HEADERS)
        
        payload = {
            "message": f"Add {path}",
            "content": base64_content,
            "branch": GITHUB_BRANCH
        }
        
        # If file exists (200), include its SHA for update
        if get_response.status_code == 200:
            existing_sha = get_response.json().get("sha")
            payload["sha"] = existing_sha
            payload["message"] = f"Update {path}"
        
        # Upload/update the file
        response = requests.put(url, json=payload, headers=HEADERS)
        
        # GitHub returns 201 for created, 200 for updated
        if response.status_code in [200, 201]:
            action = "Updated" if get_response.status_code == 200 else "Created"
            return {
                "success": True,
                "status": response.status_code,
                "message": f"{action} successfully"
            }
        else:
            error_msg = f"Status {response.status_code}: {response.text[:500]}"
            print(f"GitHub upload failed for {path}: {error_msg}")
            return {
                "success": False,
                "status": response.status_code,
                "message": error_msg
            }
            
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"Exception uploading {path}: {error_msg}")
        return {
            "success": False,
            "status": 0,
            "message": error_msg
        }

def delete_file(path, sha):
    """Delete a file from GitHub repository
    
    Args:
        path: File path in repository
        sha: File SHA hash
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    
    try:
        response = requests.delete(url, json={
            "message": f"Delete {path}",
            "sha": sha,
            "branch": GITHUB_BRANCH
        }, headers=HEADERS)
        
        # GitHub returns 200 for successful deletion
        if response.status_code == 200:
            return True
        else:
            print(f"GitHub delete failed for {path}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception deleting {path}: {str(e)}")
        return False