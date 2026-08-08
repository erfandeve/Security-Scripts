import os
import re
import argparse
from colorama import init, Fore, Style

init(autoreset=True)
# ==========================================
# scanner configurations
# ==========================================
PATTERNS = {
    "Stripe API Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Generic 32-char Token": r"\b[a-fA-F0-9]{32}\b",
    "AWS Access Key": r"\b(AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b"
}

IGNORE_DIRS = {'.git', '.idea', '__pycache__', 'venv', '.venv', 'env', 'node_modules'}
IGNORE_EXTENSIONS = {'.jpg', '.png', '.exe', '.pdf', '.zip', '.mp4'}


# ==========================================
# main script functions
# ==========================================
def scan_file(filepath):
    found_secrets = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                for secret_type, pattern in PATTERNS.items():
                    matches = re.findall(pattern, line)
                    for match in matches:
                        found_secrets.append({
                            'type': secret_type,
                            'secret': match,
                            'line': line_number
                        })
    except (UnicodeDecodeError, PermissionError):
        pass
    return found_secrets


def scan_directory(directory_path):
    # getting the path and making it beautiful
    abs_path = os.path.abspath(directory_path)
    print(f"{Fore.CYAN} scanning the Directory🔍: {abs_path} ...\n")
    secrets_found_total = 0

    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file_name in files:
            _, ext = os.path.splitext(file_name)
            if ext.lower() in IGNORE_EXTENSIONS:
                continue

            filepath = os.path.join(root, file_name)
            secrets = scan_file(filepath)

            if secrets:
                print(f"{Fore.RED}🚨 Risk of data leakage in the file: {filepath}")
                for s in secrets:
                    secrets_found_total += 1
                    print(f"{Fore.YELLOW}   -> line  {s['line']} | type : {s['type']} | value : {s['secret']}")

    if secrets_found_total == 0:
        print("{Fore.GREEN}{Style.BRIGHT} ✅ Done. No sensitive keys were found.")
    else:
        print(f"\n{Fore.RED}{Style.BRIGHT} Done. {secrets_found_total} Sensitive keys were found.⚠️")


# ==========================================
# (CLI) Command Line Interface
# ==========================================
if __name__ == "__main__":
    # Setting up the parser
    parser = argparse.ArgumentParser(
        description="🛡️ Security scanning tool for finding leaked API keys and sensitive information in source code."
    )

    # Adding the path argument (Path)
    parser.add_argument(
        "-p", "--path",
        default=".",
        help="The path to be scanned (default: current directory)"
    )

    # Reading user commands from the terminal
    args = parser.parse_args()

    # Executing the program with the path entered by the user.
    scan_directory(args.path)