import requests
from settings import *

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Brainsta-Admin"
}

def list_files(path):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def upload_file(path, base64_content):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    requests.put(url, json={
        "message": f"Add {path}",
        "content": base64_content,
        "branch": GITHUB_BRANCH
    }, headers=HEADERS)

def delete_file(path, sha):
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    requests.delete(url, json={
        "message": f"Delete {path}",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }, headers=HEADERS)
