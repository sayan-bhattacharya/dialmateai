# env_test.py
from dotenv import load_dotenv
import os

def print_env_vars():
    load_dotenv()

    # Print all environment variables (careful not to share sensitive info)
    print("Environment Variables:")
    print(f"MONGODB_URI exists: {'MONGODB_URI' in os.environ}")
    print(f"DB_NAME exists: {'DB_NAME' in os.environ}")
    print(f"DB_NAME value: {os.getenv('DB_NAME')}")

    # Print masked version of MongoDB URI for verification
    mongodb_uri = os.getenv('MONGODB_URI', '')
    if mongodb_uri:
        parts = mongodb_uri.split('@')
        if len(parts) > 1:
            masked_uri = f"...@{parts[1]}"
            print(f"MongoDB URI (masked): {masked_uri}")

if __name__ == "__main__":
    print_env_vars()