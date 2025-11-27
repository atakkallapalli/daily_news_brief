#!/usr/bin/env python3
"""
AWS Bedrock Connection Test Script
Tests connection to Bedrock Claude Haiku 3
"""

import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test AWS credentials"""
    print("🔍 Testing AWS Credentials...")
    
    try:
        # Test STS (Security Token Service) to verify credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Credentials Valid")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User ARN: {identity.get('Arn', 'Unknown')}")
        print(f"   User ID: {identity.get('UserId', 'Unknown')}")
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False

def test_bedrock_access():
    """Test Bedrock service access"""
    print("\n🔍 Testing Bedrock Access...")
    
    try:
        # Test Bedrock service access
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        models = bedrock.list_foundation_models()
        
        print(f"✅ Bedrock Service Access Valid")
        print(f"   Available models: {len(models.get('modelSummaries', []))}")
        
        # Check for Claude Haiku 3 specifically
        claude_models = [m for m in models.get('modelSummaries', []) 
                        if 'claude-3-haiku' in m.get('modelId', '')]
        
        if claude_models:
            print(f"✅ Claude Haiku 3 Available")
            for model in claude_models:
                print(f"   Model: {model.get('modelId')}")
        else:
            print("⚠️  Claude Haiku 3 not found - may need to request access")
        
        return True
        
    except ClientError as e:
        print(f"❌ Bedrock access error: {e}")
        if 'AccessDenied' in str(e):
            print("   Check IAM permissions for bedrock:ListFoundationModels")
        return False

def test_bedrock_runtime():
    """Test Bedrock Runtime (model invocation)"""
    print("\n🔍 Testing Bedrock Runtime...")
    
    try:
        # Test Bedrock Runtime
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare test request
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'Bedrock connection successful'"
                }
            ]
        }
        
        # Test Claude Haiku 3 invocation
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        print(f"✅ Bedrock Runtime Working")
        print(f"   Model: anthropic.claude-3-haiku-20240307-v1:0")
        print(f"   Response: {content}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Bedrock Runtime error: {e}")
        if 'AccessDenied' in str(e):
            print("   Check IAM permissions for bedrock:InvokeModel")
        elif 'ValidationException' in str(e):
            print("   Model may not be available in this region")
        return False

def main():
    """Main test function"""
    print("🧪 AWS Bedrock Connection Test")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION', 'AWS_PROFILE']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                print(f"   {var}: {value[:10]}...")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: Not set")
    
    # Run tests
    creds_ok = test_aws_credentials()
    if not creds_ok:
        print("\n❌ Cannot proceed without valid AWS credentials")
        return
    
    bedrock_ok = test_bedrock_access()
    runtime_ok = test_bedrock_runtime()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary")
    print("=" * 50)
    print(f"AWS Credentials: {'✅ Pass' if creds_ok else '❌ Fail'}")
    print(f"Bedrock Access: {'✅ Pass' if bedrock_ok else '❌ Fail'}")
    print(f"Bedrock Runtime: {'✅ Pass' if runtime_ok else '❌ Fail'}")
    
    if creds_ok and bedrock_ok and runtime_ok:
        print("\n🎉 All tests passed! Ready to use Bedrock Claude Haiku 3")
        print("   Run: python3 sf_executive_bedrock_digest.py")
    else:
        print("\n⚠️  Some tests failed. Check AWS setup and permissions.")

if __name__ == "__main__":
    main()
