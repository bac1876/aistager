import os

# Check which files exist
files_to_check = ['app.py', 'main.py', 'app_with_webhook.py']

print("=== Checking which Python files exist ===")
for file in files_to_check:
    if os.path.exists(file):
        print(f"✓ {file} exists")
        # Check first few lines
        with open(file, 'r') as f:
            lines = f.readlines()[:5]
            for i, line in enumerate(lines):
                if 'webhook' in line.lower() or 'debug' in line.lower() or 'ngrok' in line.lower():
                    print(f"  Line {i+1}: {line.strip()}")
    else:
        print(f"✗ {file} does not exist")

print("\n=== Checking if main.py is being imported ===")
try:
    import main
    print("main.py can be imported")
except:
    print("main.py cannot be imported")

print("\n=== Current working directory ===")
print(os.getcwd())