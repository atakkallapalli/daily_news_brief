

#!/usr/bin/env python3
"""
AWS Credentials Setup Script for Bedrock Integration
Creates and configures AWS credentials for SF Executive Digest
"""

import os
import json
from pathlib import Path
from datetime import datetime

def create_aws_credentials_setup():
    """Create comprehensive AWS credentials setup"""
    
    print("🔧 AWS Credentials Setup for Bedrock Integration")
    print("=" * 60)
    
    # Get user's home directory
    home_dir = Path.home()
    aws_dir = home_dir / ".aws"
    
    print(f"AWS configuration directory: {aws_dir}")
    
    # Create .aws directory if it doesn't exist
    aws_dir.mkdir(exist_ok=True)
    print(f"✅ Created/verified AWS directory: {aws_dir}")
    
    # Paths for AWS files
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    # Check existing files
    credentials_exists = credentials_file.exists()
    config_exists = config_file.exists()
    
    print(f"\nExisting files:")
    print(f"  credentials: {'✅ exists' if credentials_exists else '❌ not found'}")
    print(f"  config: {'✅ exists' if config_exists else '❌ not found'}")
    
    # Create backup if files exist
    if credentials_exists:
        backup_creds = credentials_file.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        credentials_file.rename(backup_creds)
        print(f"📦 Backed up existing credentials to: {backup_creds}")
    
    if config_exists:
        backup_config = config_file.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        config_file.rename(backup_config)
        print(f"📦 Backed up existing config to: {backup_config}")
    
    # Create new credentials file
    credentials_content = """[default]
aws_access_key_id = YOUR_AWS_ACCESS_KEY_ID_HERE
aws_secret_access_key = YOUR_AWS_SECRET_ACCESS_KEY_HERE

[bedrock-sf-digest]
aws_access_key_id = YOUR_BEDROCK_ACCESS_KEY_ID_HERE
aws_secret_access_key = YOUR_BEDROCK_SECRET_ACCESS_KEY_HERE

[sf-executive]
aws_access_key_id = YOUR_SF_EXECUTIVE_ACCESS_KEY_ID_HERE
aws_secret_access_key = YOUR_SF_EXECUTIVE_SECRET_ACCESS_KEY_HERE
"""
    
    with open(credentials_file, 'w') as f:
        f.write(credentials_content)
    
    # Set proper permissions (readable only by user)
    credentials_file.chmod(0o600)
    print(f"✅ Created credentials file: {credentials_file}")
    
    # Create new config file
    config_content = """[default]
region = us-west-2
output = json

[profile bedrock-sf-digest]
region = us-west-2
output = json

[profile sf-executive]
region = us-west-2
output = json
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    config_file.chmod(0o644)
    print(f"✅ Created config file: {config_file}")
    
    return credentials_file, config_file

def create_environment_setup_script():
    """Create environment variable setup script"""
    
    env_script_content = """#!/bin/bash
# AWS Credentials Environment Variables Setup
# Source this file to set up AWS credentials for Bedrock

echo "🔧 Setting up AWS credentials for Bedrock..."

# Option 1: Set AWS credentials directly
export AWS_ACCESS_KEY_ID="your-aws-access-key-id-here"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key-here"
export AWS_DEFAULT_REGION="us-west-2"

# Option 2: Use AWS profile (alternative)
# export AWS_PROFILE="bedrock-sf-digest"

# Option 3: Use AWS session token (if using temporary credentials)
# export AWS_SESSION_TOKEN="your-session-token-here"

echo "✅ AWS environment variables set"
echo "Region: $AWS_DEFAULT_REGION"
echo "Access Key: ${AWS_ACCESS_KEY_ID:0:10}..."

# Test AWS CLI connection
echo "🧪 Testing AWS CLI connection..."
aws sts get-caller-identity 2>/dev/null && echo "✅ AWS CLI working" || echo "❌ AWS CLI test failed"

# Test Bedrock access
echo "🧪 Testing Bedrock access..."
aws bedrock list-foundation-models --region us-west-2 2>/dev/null && echo "✅ Bedrock access working" || echo "❌ Bedrock access failed"
"""
    
    env_script_path = Path("setup_aws_env.sh")
    with open(env_script_path, 'w') as f:
        f.write(env_script_content)
    
    env_script_path.chmod(0o755)
    print(f"✅ Created environment setup script: {env_script_path}")
    
    return env_script_path

def create_bedrock_test_script():
    """Create Bedrock connection test script"""
    
    test_script_content = '''#!/usr/bin/env python3
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
    print("\\n🔍 Testing Bedrock Access...")
    
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
    print("\\n🔍 Testing Bedrock Runtime...")
    
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
    print("\\n📋 Environment Variables:")
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
        print("\\n❌ Cannot proceed without valid AWS credentials")
        return
    
    bedrock_ok = test_bedrock_access()
    runtime_ok = test_bedrock_runtime()
    
    # Summary
    print("\\n" + "=" * 50)
    print("🎯 Test Summary")
    print("=" * 50)
    print(f"AWS Credentials: {'✅ Pass' if creds_ok else '❌ Fail'}")
    print(f"Bedrock Access: {'✅ Pass' if bedrock_ok else '❌ Fail'}")
    print(f"Bedrock Runtime: {'✅ Pass' if runtime_ok else '❌ Fail'}")
    
    if creds_ok and bedrock_ok and runtime_ok:
        print("\\n🎉 All tests passed! Ready to use Bedrock Claude Haiku 3")
        print("   Run: python3 sf_executive_bedrock_digest.py")
    else:
        print("\\n⚠️  Some tests failed. Check AWS setup and permissions.")

if __name__ == "__main__":
    main()
'''
    
    test_script_path = Path("test_bedrock_connection.py")
    with open(test_script_path, 'w') as f:
        f.write(test_script_content)
    
    test_script_path.chmod(0o755)
    print(f"✅ Created Bedrock test script: {test_script_path}")
    
    return test_script_path

def create_iam_policy_template():
    """Create IAM policy template for Bedrock access"""
    
    iam_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockFoundationModelAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:ListFoundationModels",
                    "bedrock:GetFoundationModel"
                ],
                "Resource": "*"
            },
            {
                "Sid": "BedrockClaudeHaikuInvoke",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
                ]
            },
            {
                "Sid": "STSGetCallerIdentity",
                "Effect": "Allow",
                "Action": [
                    "sts:GetCallerIdentity"
                ],
                "Resource": "*"
            }
        ]
    }
    
    policy_path = Path("bedrock_iam_policy.json")
    with open(policy_path, 'w') as f:
        json.dump(iam_policy, f, indent=2)
    
    print(f"✅ Created IAM policy template: {policy_path}")
    
    return policy_path

def create_setup_instructions():
    """Create comprehensive setup instructions"""
    
    instructions = """# AWS Bedrock Credentials Setup Instructions

## Quick Start

### 1. Get AWS Credentials
- Log into AWS Console
- Go to IAM → Users → Your User → Security Credentials
- Create Access Key (or use existing)
- Note down Access Key ID and Secret Access Key

### 2. Set Up Credentials (Choose One Method)

#### Method A: Environment Variables (Recommended)
```bash
# Set environment variables
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"

# Test the setup
python3 test_bedrock_connection.py
```

#### Method B: AWS Credentials File
```bash
# Edit the generated credentials file
nano ~/.aws/credentials

# Add your actual keys:
[default]
aws_access_key_id = AKIA...your-actual-key
aws_secret_access_key = your-actual-secret-key

[bedrock-sf-digest]
aws_access_key_id = AKIA...your-bedrock-key
aws_secret_access_key = your-bedrock-secret-key
```

#### Method C: Use Setup Script
```bash
# Source the environment setup script
source setup_aws_env.sh

# Edit the script first to add your actual credentials
nano setup_aws_env.sh
```

### 3. Configure IAM Permissions

#### Create IAM Policy:
1. Go to AWS Console → IAM → Policies
2. Create Policy → JSON
3. Copy content from `bedrock_iam_policy.json`
4. Name it "BedrockSFDigestPolicy"
5. Attach to your user or role

#### Required Permissions:
- `bedrock:ListFoundationModels`
- `bedrock:InvokeModel`
- `sts:GetCallerIdentity`

### 4. Enable Claude Haiku 3 Access

#### Check Model Access:
1. Go to AWS Console → Bedrock
2. Navigate to "Foundation Models"
3. Find "Claude 3 Haiku" by Anthropic
4. Click "Request model access" if needed
5. Wait for approval (usually instant)

### 5. Test Connection

```bash
# Test AWS credentials
python3 test_bedrock_connection.py

# If successful, run SF digest
python3 sf_executive_bedrock_digest.py
```

## Troubleshooting

### Common Issues:

**"No credentials found"**
- Check environment variables: `echo $AWS_ACCESS_KEY_ID`
- Verify credentials file: `cat ~/.aws/credentials`
- Try: `aws configure list`

**"Access Denied"**
- Check IAM permissions
- Ensure Bedrock service access
- Verify region (use us-west-2)

**"Model not found"**
- Request Claude 3 Haiku access in AWS Console
- Check region availability
- Try different region: us-east-1

**"Invalid credentials"**
- Regenerate access keys
- Check for typos in keys
- Ensure keys are active

### Regional Availability:
- **Primary**: us-west-2 (Oregon)
- **Secondary**: us-east-1 (Virginia)
- **Check**: `aws bedrock list-foundation-models --region us-west-2`

### Cost Estimates:
- Claude Haiku 3: ~$0.25 per 1M input tokens
- Typical digest: ~$0.01-0.05 per generation
- Set billing alerts in AWS Console

## Security Best Practices

### Credential Security:
- Never commit credentials to git
- Use IAM roles in production
- Rotate keys regularly
- Use least privilege permissions

### File Permissions:
```bash
# Secure credentials file
chmod 600 ~/.aws/credentials
chmod 644 ~/.aws/config
```

### Environment Variables:
```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export AWS_ACCESS_KEY_ID="your-key"' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY="your-secret"' >> ~/.bashrc
echo 'export AWS_DEFAULT_REGION="us-west-2"' >> ~/.bashrc
```

## Files Created:
- ✅ `~/.aws/credentials` - AWS credentials
- ✅ `~/.aws/config` - AWS configuration  
- ✅ `setup_aws_env.sh` - Environment setup script
- ✅ `test_bedrock_connection.py` - Connection test
- ✅ `bedrock_iam_policy.json` - IAM policy template

## Next Steps:
1. Set up credentials using preferred method
2. Run connection test
3. Generate SF executive digest
4. Set up scheduled generation (optional)

---
**Status**: Ready for AWS Bedrock Claude Haiku 3 integration
**Support**: Check BEDROCK_SETUP_GUIDE.md for detailed documentation
"""
    
    instructions_path = Path("AWS_CREDENTIALS_SETUP.md")
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Created setup instructions: {instructions_path}")
    
    return instructions_path

def main():
    """Main setup function"""
    
    print("🚀 AWS Bedrock Credentials Setup")
    print("=" * 60)
    
    # Create all setup files
    print("\n1. Setting up AWS credentials files...")
    creds_file, config_file = create_aws_credentials_setup()
    
    print("\n2. Creating environment setup script...")
    env_script = create_environment_setup_script()
    
    print("\n3. Creating Bedrock test script...")
    test_script = create_bedrock_test_script()
    
    print("\n4. Creating IAM policy template...")
    policy_file = create_iam_policy_template()
    
    print("\n5. Creating setup instructions...")
    instructions_file = create_setup_instructions()
    
    print("\n" + "=" * 60)
    print("✅ AWS Bedrock Setup Complete!")
    print("=" * 60)
    
    print(f"\n📁 Files Created:")
    print(f"   • {creds_file} - AWS credentials")
    print(f"   • {config_file} - AWS config")
    print(f"   • {env_script} - Environment setup")
    print(f"   • {test_script} - Connection test")
    print(f"   • {policy_file} - IAM policy")
    print(f"   • {instructions_file} - Setup guide")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Edit credentials file with your AWS keys:")
    print(f"      nano {creds_file}")
    print(f"   2. Test connection:")
    print(f"      python3 {test_script}")
    print(f"   3. Generate SF digest:")
    print(f"      python3 sf_executive_bedrock_digest.py")
    
    print(f"\n🔒 Security Notes:")
    print(f"   • Credentials file permissions set to 600 (user only)")
    print(f"   • Never commit credentials to version control")
    print(f"   • Use IAM roles in production environments")
    
    print(f"\n📖 Documentation:")
    print(f"   • Read: {instructions_file}")
    print(f"   • Full guide: BEDROCK_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()


