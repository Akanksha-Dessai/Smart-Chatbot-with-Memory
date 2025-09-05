#!/usr/bin/env python3
"""
Example test script for the Smart Chatbot Backend
Run this to test the API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_simple_chat():
    """Test simple chat endpoint"""
    print("\nTesting simple chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/simple",
            json={
                "user_id": "test_user",
                "message": "Hello, how are you today?"
            }
        )
        print(f"Chat Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User ID: {data['user_id']}")
            print(f"Message: {data['message']}")
            print(f"Response: {data['response']}")
            print(f"Timestamp: {data['timestamp']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Simple chat test failed: {e}")
        return False

def test_streaming_chat():
    """Test streaming chat endpoint"""
    print("\nTesting streaming chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "user_id": "test_user",
                "message": "Tell me a short story about a robot"
            },
            stream=True
        )
        print(f"Streaming Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            print("\n[Stream completed]")
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get('content'):
                                print(chunk['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Streaming chat test failed: {e}")
        return False

def test_chat_history():
    """Test chat history endpoint"""
    print("\nTesting chat history endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/history/test_user")
        print(f"History Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User ID: {data['user_id']}")
            print(f"History Count: {data['count']}")
            if data['history']:
                print("Recent conversations:")
                for conv in data['history'][-2:]:  # Show last 2 conversations
                    print(f"  - User: {conv['user_message']}")
                    print(f"    Bot: {conv['assistant_response'][:50]}...")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Chat history test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Smart Chatbot Backend - API Test Suite")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Simple Chat", test_simple_chat),
        ("Streaming Chat", test_streaming_chat),
        ("Chat History", test_chat_history)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    print(f"\n{'='*50}")
    print("Test Results Summary:")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()
