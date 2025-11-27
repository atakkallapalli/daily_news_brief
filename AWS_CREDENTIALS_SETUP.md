# AWS Bedrock Credentials Setup Instructions

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
