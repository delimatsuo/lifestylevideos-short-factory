#!/usr/bin/env python3
"""
Debug Reddit API connection
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_reddit_public():
    """Test Reddit public API without authentication"""
    print("🔍 Testing Reddit Public API...")
    
    headers = {
        'User-Agent': 'ShortsFactory/1.0'
    }
    
    try:
        # Test simple public endpoint
        response = requests.get(
            'https://www.reddit.com/r/python/hot.json?limit=1',
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Reddit public API working")
            if 'data' in data and 'children' in data['data']:
                children = data['data']['children']
                if children:
                    post = children[0]['data']
                    print(f"Sample post: {post.get('title', 'No title')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reddit_auth():
    """Test Reddit API with authentication"""
    print("\n🔐 Testing Reddit API Authentication...")
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'*' * len(client_secret) if client_secret else 'None'}")
    
    if not client_id or not client_secret:
        print("❌ Missing credentials")
        return False
    
    try:
        # Reddit OAuth
        auth_response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            data={'grant_type': 'client_credentials'},
            auth=(client_id, client_secret),
            headers={'User-Agent': 'ShortsFactory/1.0'}
        )
        
        print(f"Auth Status: {auth_response.status_code}")
        print(f"Auth Response: {auth_response.text}")
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            access_token = token_data.get('access_token')
            print("✅ Authentication successful")
            print(f"Token type: {token_data.get('token_type')}")
            print(f"Expires in: {token_data.get('expires_in')} seconds")
            
            # Test API call with token
            api_response = requests.get(
                'https://oauth.reddit.com/r/python/hot?limit=1',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'User-Agent': 'ShortsFactory/1.0'
                }
            )
            
            print(f"API Call Status: {api_response.status_code}")
            if api_response.status_code == 200:
                print("✅ Authenticated API call successful")
                return True
            else:
                print(f"❌ API call failed: {api_response.text}")
                return False
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False

if __name__ == '__main__':
    print("🐍 Reddit API Debug Test")
    print("=" * 30)
    
    public_works = test_reddit_public()
    auth_works = test_reddit_auth()
    
    print(f"\n📊 Results:")
    print(f"Public API: {'✅' if public_works else '❌'}")
    print(f"Authenticated API: {'✅' if auth_works else '❌'}")
    
    if public_works or auth_works:
        print("\n✅ Reddit API is accessible!")
        print("The 403 error might be from specific subreddits or rate limiting")
        print("Try running the full test again")
    else:
        print("\n❌ Reddit API issues detected")
        print("Check credentials and network connection")
