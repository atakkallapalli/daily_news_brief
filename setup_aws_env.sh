#!/bin/bash
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
