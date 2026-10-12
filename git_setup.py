import os
import dulwich.porcelain as porcelain

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def init_and_commit():
    print(f"Initializing Git repository in {REPO_DIR}...")
    try:
        repo = porcelain.open_repo(REPO_DIR)
        print("Git repository already exists.")
    except Exception:
        repo = porcelain.init(REPO_DIR)
        print("Git repository initialized successfully.")

    print("Adding project files to Git...")
    porcelain.add(repo, paths=[
        'app.py',
        'database.py',
        'sample_data.py',
        'test_system.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'run_app.bat',
        'run_public_tunnel.bat',
        'templates',
        'static'
    ])

    print("Creating initial commit...")
    try:
        commit_id = porcelain.commit(
            repo, 
            message=b"Initial commit: Gym Membership Management System with Python & SQLite",
            author=b"Jethro Cabal <developer@local>",
            committer=b"Jethro Cabal <developer@local>"
        )
        print(f"Committed successfully! Commit hash: {commit_id.decode('ascii')[:7]}")
    except Exception as e:
        print(f"Commit note: {e}")

    # Set default branch to main
    try:
        repo.refs[b'refs/heads/main'] = repo.head()
    except Exception:
        pass

    print("\nGit repository is ready for GitHub!")

def push_to_remote(remote_url, username=None, password_or_token=None):
    repo = porcelain.open_repo(REPO_DIR)
    print(f"Setting remote origin: {remote_url}")
    try:
        porcelain.remote_add(repo, 'origin', remote_url)
    except Exception:
        pass # Already exists
    
    print(f"Pushing to {remote_url}...")
    kwargs = {}
    if username and password_or_token:
        kwargs['username'] = username
        kwargs['password'] = password_or_token
        
    porcelain.push(repo, remote_location=remote_url, refspecs=[b'refs/heads/main:refs/heads/main'], **kwargs)
    print("Push to GitHub completed successfully!")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'push':
        if len(sys.argv) < 3:
            print("Usage: python git_setup.py push <github_remote_url> [username] [token]")
        else:
            url = sys.argv[2]
            user = sys.argv[3] if len(sys.argv) > 3 else None
            pwd = sys.argv[4] if len(sys.argv) > 4 else None
            push_to_remote(url, user, pwd)
    else:
        init_and_commit()
