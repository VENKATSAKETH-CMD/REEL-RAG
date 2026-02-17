#!/usr/bin/env python
"""
Integration Test Script - Manual Testing Guide

This script documents the steps to manually test the entire system end-to-end:
1. Register a user
2. Upload a video
3. Wait for processing
4. Ask questions about the video
5. Receive consistent answers

SETUP:
1. Ensure backend is running: cd backend && python -m uvicorn app.main:app --reload
2. Ensure PostgreSQL is running with pgvector
3. Copy .env.example to .env and set DATABASE_URL to your PostgreSQL instance
4. Install dependencies: pip install -r requirements.txt

USAGE:
1. Run this script: python test_integration.py
2. Or run individual tests manually using the curl commands below

Manual Testing with curl:
---------------------------

# 1. REGISTER A USER
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Response should include JWT token
# Save the token as: TOKEN="..."


# 2. UPLOAD A VIDEO
# Create a dummy video file: dd if=/dev/zero of=test.mp4 bs=1M count=1

curl -X POST http://localhost:8000/reels \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp4" \
  -F "title=Test Video"

# Response should include reel_id
# Save the ID as: REEL_ID="1"


# 3. CHECK PROCESSING STATUS
# Wait a few seconds, then check status

curl -X GET http://localhost:8000/reels/$REEL_ID \
  -H "Authorization: Bearer $TOKEN"

# Status should progress: uploaded -> processing -> ready
# (or failed if something went wrong)


# 4. ASK A QUESTION ABOUT THE VIDEO
# Once status is "ready", you can ask questions

curl -X POST http://localhost:8000/reels/$REEL_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What was discussed in the video?"
  }'

# Response should include an answer field with text


# 5. VERIFY RAG CONSISTENCY
# The answer should be based on the transcript chunks
# (In stub mode, the transcript is deterministic based on filename)

"""

import os
import sys
import time
import json
import requests
from pathlib import Path

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = "test_integration@example.com"
TEST_PASSWORD = "testpass123"

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def log_info(msg: str):
    print(f"{GREEN}ℹ️  {msg}{RESET}")


def log_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")


def log_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")


def log_warn(msg: str):
    print(f"{YELLOW}⚠️  {msg}{RESET}")


def test_health():
    """Test: API health check"""
    log_info("Testing health check...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            log_success("Health check passed")
            return True
        else:
            log_error(f"Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"Health check error: {e}")
        return False


def test_register():
    """Test: User registration"""
    log_info(f"Registering test user: {TEST_EMAIL}")
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10,
        )
        if resp.status_code == 200:
            log_success("User registered")
            return True
        elif resp.status_code == 400:
            log_warn("User already exists (assuming previous test)")
            return True
        else:
            log_error(f"Registration failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log_error(f"Registration error: {e}")
        return False


def test_login():
    """Test: User login"""
    log_info("Logging in...")
    try:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            log_success(f"Login successful, token: {token[:20]}...")
            return token
        else:
            log_error(f"Login failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        log_error(f"Login error: {e}")
        return None


def test_upload(token: str):
    """Test: Video upload"""
    log_info("Creating test video file...")
    test_file = Path("test_video.mp4")
    
    # Create a small test file
    try:
        with open(test_file, "wb") as f:
            f.write(b"\x00" * 1024)  # 1KB dummy file
        log_info(f"Test file created: {test_file}")
    except Exception as e:
        log_error(f"Could not create test file: {e}")
        return None
    
    log_info("Uploading video...")
    try:
        with open(test_file, "rb") as f:
            files = {"file": ("test_video.mp4", f, "video/mp4")}
            data = {"title": "Test Reel"}
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.post(
                f"{BASE_URL}/reels",
                files=files,
                data=data,
                headers=headers,
                timeout=30,
            )
        
        if resp.status_code == 200:
            reel_data = resp.json()
            reel_id = reel_data.get("id")
            log_success(f"Video uploaded, reel_id: {reel_id}, status: {reel_data.get('status')}")
            return reel_id
        else:
            log_error(f"Upload failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        log_error(f"Upload error: {e}")
        return None
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def test_processing(reel_id: int, token: str, max_wait: int = 30):
    """Test: Wait for reel to be processed"""
    log_info(f"Waiting for reel {reel_id} to be processed (max {max_wait}s)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(
                f"{BASE_URL}/reels/{reel_id}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                reel = resp.json()
                status = reel.get("status")
                log_info(f"  Current status: {status}")
                
                if status == "ready":
                    log_success(f"Reel {reel_id} is ready for chat")
                    return True
                elif status == "failed":
                    log_error(f"Reel {reel_id} failed to process")
                    return False
                
                time.sleep(2)
            else:
                log_error(f"Get reel failed: {resp.status_code}")
                return False
        except Exception as e:
            log_error(f"Get reel error: {e}")
            return False
    
    log_error(f"Reel did not finish processing within {max_wait}s")
    return False


def test_chat(reel_id: int, token: str, question: str = "What is in this video?"):
    """Test: Chat about reel"""
    log_info(f"Asking question: '{question}'")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.post(
            f"{BASE_URL}/reels/{reel_id}/chat",
            json={"message": question},
            headers=headers,
            timeout=30,
        )
        
        if resp.status_code == 200:
            chat_response = resp.json()
            answer = chat_response.get("answer", "")
            log_success(f"Answer received ({len(answer)} chars)")
            print(f"\n  Answer: {answer[:200]}...\n")
            return True
        else:
            log_error(f"Chat failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log_error(f"Chat error: {e}")
        return False


def main():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("Reel RAG Integration Test")
    print("="*80 + "\n")
    
    print(f"API Base URL: {BASE_URL}\n")
    
    # Check API is running
    if not test_health():
        log_error("API is not running. Start with: python -m uvicorn app.main:app --reload")
        return False
    
    # Register
    if not test_register():
        return False
    
    # Login
    token = test_login()
    if not token:
        return False
    
    # Upload
    reel_id = test_upload(token)
    if not reel_id:
        return False
    
    # Wait for processing
    if not test_processing(reel_id, token):
        return False
    
    # Chat
    if not test_chat(reel_id, token):
        return False
    
    print("\n" + "="*80)
    log_success("ALL TESTS PASSED")
    print("="*80 + "\n")
    
    print("Manual test commands (for debugging):")
    print(f"\n  TOKEN=$(curl -s -X POST {BASE_URL}/auth/login \\")
    print(f"    -d 'username={TEST_EMAIL}&password={TEST_PASSWORD}' | jq -r '.access_token')")
    print(f"\n  # Upload video:")
    print(f"  curl -X POST {BASE_URL}/reels \\")
    print(f"    -H \"Authorization: Bearer $TOKEN\" \\")
    print(f"    -F 'file=@your-video.mp4' \\")
    print(f"    -F 'title=Your Video'")
    print(f"\n  # Chat:")
    print(f"  curl -X POST {BASE_URL}/reels/1/chat \\")
    print(f"    -H \"Authorization: Bearer $TOKEN\" \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -d '{{\"message\": \"What is in the video?\"}}'")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
