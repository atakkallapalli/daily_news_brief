

# AWS Bedrock Claude Haiku 3 Setup Guide
## San Francisco Executive News Summary Generator

### Overview
The SF Executive Bedrock Digest uses AWS Bedrock with Claude Haiku 3 to generate executive-level news summaries focused on San Francisco Bay Area technology, business, and innovation news.

### Features
- ✅ **AWS Bedrock Integration**: Uses Claude Haiku 3 via AWS Bedrock API
- ✅ **SF Bay Area Focus**: Filters for local technology and business news
- ✅ **Executive Format**: Strategic insights and actionable recommendations
- ✅ **Enhanced Fallback**: Works without AWS credentials using intelligent fallback
- ✅ **Cost Effective**: Claude Haiku 3 is optimized for speed and cost efficiency

### AWS Bedrock Setup

#### 1. AWS Account Requirements
- Active AWS account with billing enabled
- Access to AWS Bedrock service (available in select regions)
- Appropriate IAM permissions for Bedrock

#### 2. Enable Claude Haiku 3 Model
```bash
# Check available regions for Bedrock
aws bedrock list-foundation-models --region us-west-2

# Enable Claude Haiku 3 model access (if needed)
# This may require requesting access through AWS Console
```

#### 3. Set Environment Variables
```bash
# Required AWS credentials
export AWS_ACCESS_KEY_ID="your-aws-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"  # Recommended for SF focus

# Optional: AWS Session Token (if using temporary credentials)
export AWS_SESSION_TOKEN="your-session-token"
```

#### 4. IAM Permissions Required
Create an IAM policy with the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

### Usage Instructions

#### Basic Usage
```bash
# Generate SF executive digest with Bedrock
python3 sf_executive_bedrock_digest.py
```

#### With AWS Credentials Set
```bash
# Set credentials and generate
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-west-2"
python3 sf_executive_bedrock_digest.py
```

#### Testing AWS Connection
```bash
# Test Bedrock connectivity
python3 -c "
import boto3
import json
from botocore.exceptions import ClientError

try:
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # Test with a simple prompt
    body = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 100,
        'temperature': 0.3,
        'messages': [{'role': 'user', 'content': 'Hello, Claude!'}]
    }
    
    response = client.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps(body),
        contentType='application/json',
        accept='application/json'
    )
    
    result = json.loads(response['body'].read())
    print('✅ Bedrock Claude Haiku 3 connection successful!')
    print(f'Response: {result[\"content\"][0][\"text\"]}')
    
except ClientError as e:
    print(f'❌ AWS Bedrock error: {e}')
except Exception as e:
    print(f'❌ Connection error: {e}')
"
```

### Model Specifications

#### Claude Haiku 3 (anthropic.claude-3-haiku-20240307-v1:0)
- **Speed**: Fastest Claude 3 model
- **Cost**: Most cost-effective option
- **Context**: 200K token context window
- **Strengths**: Quick responses, good for summaries and analysis
- **Use Case**: Perfect for daily news digests and executive summaries

#### Pricing (Approximate)
- **Input**: ~$0.25 per 1M tokens
- **Output**: ~$1.25 per 1M tokens
- **Typical Digest**: ~$0.01-0.05 per generation

### Regional Availability

#### Recommended Regions for SF Focus:
1. **us-west-2** (Oregon) - Recommended for SF Bay Area
2. **us-east-1** (Virginia) - Alternative option
3. **us-west-1** (California) - If available

#### Check Model Availability:
```bash
aws bedrock list-foundation-models --region us-west-2 --query 'modelSummaries[?contains(modelId, `claude-3-haiku`)]'
```

### Troubleshooting

#### Common Issues:

**1. "Model not found" Error**
```bash
# Solution: Check model availability in your region
aws bedrock list-foundation-models --region us-west-2
```

**2. "Access Denied" Error**
- Verify IAM permissions include `bedrock:InvokeModel`
- Check if model access is enabled in AWS Console
- Ensure you're using the correct region

**3. "Credentials not found" Error**
```bash
# Verify credentials are set
aws configure list
# Or check environment variables
echo $AWS_ACCESS_KEY_ID
```

**4. "Region not supported" Error**
- Try different regions: us-west-2, us-east-1
- Check AWS Bedrock service availability

### Fallback Behavior

#### When Bedrock is Unavailable:
- ✅ Automatically switches to enhanced fallback generation
- ✅ Maintains all formatting and SF focus
- ✅ Provides executive-level insights
- ⚠️ Content is rule-based rather than LLM-generated

#### Fallback Triggers:
- AWS credentials not configured
- Bedrock service unavailable
- Model access denied
- Network connectivity issues
- API rate limits exceeded

### Output Format

#### Generated Files:
- **Filename**: `sf_executive_bedrock_digest_YYYY-MM-DD_HH-MM.md`
- **Format**: Markdown with executive summary structure
- **Content**: SF Bay Area focused business and technology news
- **Length**: Typically 12-15 articles with strategic analysis

#### Content Structure:
1. **Executive Summary**: High-level overview
2. **Key Articles**: Detailed analysis with strategic implications
3. **Strategic Insights**: Trends and recommendations
4. **Action Items**: Executive decision-making guidance

### Integration Options

#### Scheduled Generation:
```bash
# Add to crontab for daily generation at 7 AM
0 7 * * * cd /path/to/daily_news_brief && python3 sf_executive_bedrock_digest.py
```

#### API Integration:
```python
from sf_executive_bedrock_digest import SFExecutiveBedrockDigest

# Programmatic usage
generator = SFExecutiveBedrockDigest()
digest_file = generator.generate_digest()
```

### Cost Optimization

#### Tips to Minimize Costs:
1. **Use Haiku 3**: Most cost-effective Claude model
2. **Limit Articles**: Script already limits to 12 articles
3. **Optimize Prompts**: Concise prompts reduce token usage
4. **Monitor Usage**: Set up AWS billing alerts
5. **Use Fallback**: Enhanced fallback for development/testing

### Security Best Practices

#### Credential Management:
- Use IAM roles instead of access keys when possible
- Rotate access keys regularly
- Use AWS Secrets Manager for production deployments
- Never commit credentials to version control

#### Network Security:
- Use VPC endpoints for Bedrock if in AWS environment
- Implement proper firewall rules
- Monitor API usage for anomalies

### Support and Resources

#### AWS Documentation:
- [AWS Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [Claude 3 Model Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-3.html)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

#### Troubleshooting Resources:
- AWS Support (if you have a support plan)
- AWS Bedrock Community Forums
- Anthropic Claude Documentation

---

**Status**: ✅ Ready for production use with AWS Bedrock Claude Haiku 3
**Fallback**: ✅ Enhanced SF executive digest generation available
**Focus**: 🌉 San Francisco Bay Area technology and business news
**Target**: 💼 C-level executives and senior leadership

