import os
import subprocess
import getpass

def main():
    print("=" * 60)
    print("  🚀 OpenEnv — Hugging Face Space Deployer")
    print("=" * 60)
    print("It looks like your previous push failed due to an authorization issue.")
    print("The token previously used might have been read-only or invalid.\n")
    
    print("To fix this:")
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Generate a new token with WRITE permissions.")
    print("   (If using Fine-Grained, select the 'openenv-data-cleaning' space")
    print("   and ensure 'Write' is checked under Repo permissions).\n")
    
    token = getpass.getpass("Enter your new HF Token (input is hidden): ").strip()
    
    if not token.startswith("hf_"):
        print("\n❌ Error: Valid Hugging Face tokens start with 'hf_'")
        return

    # Embed the user:token in the remote URL (safely bypasses git credential manager cache issues)
    remote_url = f"https://jeevan716:{token}@huggingface.co/spaces/jeevan716/openenv-data-cleaning"
    
    print("\n[1/2] Updating 'hf' remote configuration...")
    try:
        subprocess.run(["git", "remote", "set-url", "hf", remote_url], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error setting git remote: {e}")
        return
        
    print("[2/2] Pushing to Hugging Face Spaces (this might take a minute)...")
    result = subprocess.run(["git", "push", "hf", "main"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ SUCCESS! Your Space has been successfully updated.")
        print("Your live app will be available at: https://huggingface.co/spaces/jeevan716/openenv-data-cleaning")
        
        # Cleanup: Remove the token from the .git/config URL so it's not sitting in plaintext permanently
        safe_url = "https://huggingface.co/spaces/jeevan716/openenv-data-cleaning"
        subprocess.run(["git", "remote", "set-url", "hf", safe_url], check=False)
        
    else:
        print("\n❌ PUSH FAILED. Server responded:\n")
        print(result.stderr)
        
        if "not authorized" in result.stderr.lower():
            print("\nHINT: You are still getting a 403 Forbidden. This confirms your new token")
            print("doesn't actually have WRITE permissions to that specific space repository.")
            print("Please double check the token permissions on Hugging Face!")

if __name__ == "__main__":
    main()
