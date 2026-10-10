import os
import shutil
import zipfile
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = os.path.dirname(os.path.abspath(__file__))
backend_app = os.path.join(root_dir, "backend", "app")
deploy_dir = os.path.join(root_dir, "deploy_huggingface")
deploy_app = os.path.join(deploy_dir, "app")
zip_target = os.path.join(deploy_dir, "app.zip")
hf_repo_dir = os.path.join(root_dir, "scratch", "hf_repo")

def sync_and_deploy(commit_msg: str = "Deploy Falcon 24/7 Engine: Anti-Ceiling Lock, Rule 34/62 Buffers, and Strict SL Protection"):
    print("=== STARTING AUTOMATED HUGGING FACE SYNC & DEPLOY ===")
    
    # 1. Sync backend/app -> deploy_huggingface/app
    print("[1/5] Syncing backend/app to deploy_huggingface/app...")
    os.makedirs(deploy_app, exist_ok=True)
    for f in os.listdir(backend_app):
        if f.endswith(".py"):
            src = os.path.join(backend_app, f)
            dst = os.path.join(deploy_app, f)
            shutil.copy2(src, dst)
    prompts_src = os.path.join(backend_app, "prompts")
    prompts_dst = os.path.join(deploy_app, "prompts")
    if os.path.exists(prompts_src):
        os.makedirs(prompts_dst, exist_ok=True)
        for f in os.listdir(prompts_src):
            shutil.copy2(os.path.join(prompts_src, f), os.path.join(prompts_dst, f))
    print("      Backend files synced successfully.")

    # 2. Clean __pycache__
    for root, dirs, files in os.walk(deploy_app):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)

    # 3. Create app.zip
    print("[2/5] Creating updated app.zip...")
    with zipfile.ZipFile(zip_target, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(deploy_app):
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, deploy_dir)
                z.write(full_p, rel_p)
        db_p = os.path.join(deploy_dir, "falcon.db")
        if os.path.exists(db_p):
            z.write(db_p, "falcon.db")
    print(f"      app.zip created ({os.path.getsize(zip_target)} bytes).")

    # 4. Copy deploy files to scratch/hf_repo
    print("[3/5] Copying app.zip, app.py, and database to scratch/hf_repo...")
    hf_zip = os.path.join(hf_repo_dir, "app.zip")
    shutil.copy2(zip_target, hf_zip)
    
    app_py_src = os.path.join(deploy_dir, "app.py")
    if os.path.exists(app_py_src):
        shutil.copy2(app_py_src, os.path.join(hf_repo_dir, "app.py"))
        
    db_src = os.path.join(deploy_dir, "falcon.db")
    if os.path.exists(db_src):
        shutil.copy2(db_src, os.path.join(hf_repo_dir, "falcon.db"))
        
    print("      Copied app.zip, app.py, and assets to git repo.")

    # 5. Git commit and push to Hugging Face
    print("[4/5] Checking Git status in scratch/hf_repo...")
    status = subprocess.run(["git", "-C", hf_repo_dir, "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("      No changes detected in Git repo.")
        return True

    print("[5/5] Committing and pushing to Hugging Face Space (forcing rebuild)...")
    subprocess.run(["git", "-C", hf_repo_dir, "add", "-A"], check=True)
    subprocess.run(["git", "-C", hf_repo_dir, "commit", "-m", commit_msg], check=True)
    push_res = subprocess.run(["git", "-C", hf_repo_dir, "push", "origin", "main"], capture_output=True, text=True)
    
    if push_res.returncode == 0:
        print("      SUCCESS: Pushed to Hugging Face Spaces!")
        print(push_res.stdout)
        print(push_res.stderr)
        return True
    else:
        print("      FAILED to push to Hugging Face:")
        print(push_res.stderr)
        return False

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Deploy Falcon 24/7 Engine: Anti-Ceiling Lock, Rule 34/62 Buffers, and Strict SL Protection"
    success = sync_and_deploy(msg)
    if success:
        print("\n🦅 HUGGING FACE CLOUD SCANNER IS NOW 100% UP TO DATE!")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        sys.exit(1)
