#!/usr/bin/env python3
"""
Debug script to check environment variables and settings loading
"""

import os
import sys

def debug_environment():
    print("=== Environment Variables Debug ===")
    
    # Check for OpenAI-related environment variables
    openai_vars = []
    for key, value in os.environ.items():
        if 'openai' in key.lower() or 'open_ai' in key.lower():
            openai_vars.append((key, value[:20] + "..." if len(value) > 20 else value))
    
    print(f"Found {len(openai_vars)} OpenAI-related environment variables:")
    for key, value in openai_vars:
        print(f"  {key}: {value}")
    
    # Check if .env file exists
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        print(f"\n.env file exists at: {env_file_path}")
        try:
            with open(env_file_path, 'r') as f:
                content = f.read()
                print("First 200 characters of .env file:")
                print(content[:200])
        except Exception as e:
            print(f"Error reading .env file: {e}")
    else:
        print(f"\n.env file not found at: {env_file_path}")
    
    # Try to import and test settings
    print("\n=== Testing Settings Import ===")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        from config.settings import Settings
        
        print("Settings class imported successfully")
        
        # Try to create settings instance
        try:
            settings = Settings()
            print("Settings instance created successfully")
            print(f"OpenAI API Key configured: {bool(settings.get_openai_api_key())}")
        except Exception as e:
            print(f"Error creating settings instance: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error importing settings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_environment() 