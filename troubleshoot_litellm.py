
#!/usr/bin/env python3
"""
LiteLLM Connection Troubleshooting Script
Diagnoses and provides solutions for LiteLLM connectivity issues
"""

import requests
import json
import os
import socket
import time
from datetime import datetime
import litellm

def test_network_connectivity(host, port):
    """Test basic network connectivity to host:port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def test_http_endpoint(url, timeout=10):
    """Test HTTP endpoint availability"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.text[:200],
            'headers': dict(response.headers)
        }
    except requests.exceptions.ConnectTimeout:
        return {'success': False, 'error': 'Connection timeout'}
    except requests.exceptions.ConnectionError as e:
        return {'success': False, 'error': f'Connection error: {str(e)[:100]}'}
    except Exception as e:
        return {'success': False, 'error': f'Error: {str(e)[:100]}'}

def test_litellm_proxy_endpoints():
    """Test various LiteLLM proxy endpoints"""
    endpoints = [
        'http://35.175.151.231:8250',
        'http://localhost:8250',
        'http://127.0.0.1:8250',
        'http://35.175.151.231:8000',
        'http://35.175.151.231:4000',
        'http://35.175.151.231:8080',
        'https://35.175.151.231:8250',
    ]
    
    results = {}
    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        
        # Test basic connectivity
        if endpoint.startswith('http://'):
            host = endpoint.split('://')[1].split(':')[0]
            port = int(endpoint.split(':')[-1])
            network_ok = test_network_connectivity(host, port)
            print(f"  Network connectivity: {'✅' if network_ok else '❌'}")
        
        # Test HTTP endpoints
        for path in ['/health', '/models', '/v1/models', '/']:
            url = f"{endpoint}{path}"
            result = test_http_endpoint(url, timeout=5)
            if result['success']:
                print(f"  ✅ {path}: Status {result['status_code']}")
                if path == '/models' and result['status_code'] == 200:
                    try:
                        models = json.loads(result['response'])
                        print(f"    Available models: {len(models.get('data', []))} found")
                    except:
                        pass
            else:
                print(f"  ❌ {path}: {result['error']}")
        
        results[endpoint] = result
        print()
    
    return results

def test_alternative_providers():
    """Test alternative LLM providers"""
    print("Testing alternative LLM providers...")
    
    # Test with environment variables
    providers = [
        ('OpenAI', 'gpt-3.5-turbo', 'OPENAI_API_KEY'),
        ('Anthropic', 'claude-3-haiku-20240307', 'ANTHROPIC_API_KEY'),
        ('Cohere', 'command', 'COHERE_API_KEY'),
    ]
    
    for provider_name, model, env_var in providers:
        api_key = os.getenv(env_var)
        print(f"\n{provider_name} ({model}):")
        
        if not api_key:
            print(f"  ❌ {env_var} not set")
            continue
        
        try:
            # Test with a simple completion
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                api_key=api_key,
                max_tokens=10,
                timeout=10
            )
            print(f"  ✅ {provider_name} working")
            return provider_name, model, api_key
        except Exception as e:
            print(f"  ❌ {provider_name} error: {str(e)[:100]}")
    
    return None, None, None

def create_local_litellm_config():
    """Create a local LiteLLM configuration"""
    config = {
        "model_list": [
            {
                "model_name": "gpt-3.5-turbo",
                "litellm_params": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "your-openai-key-here"
                }
            },
            {
                "model_name": "claude-3-haiku",
                "litellm_params": {
                    "model": "claude-3-haiku-20240307",
                    "api_key": "your-anthropic-key-here"
                }
            }
        ],
        "general_settings": {
            "master_key": "sk-12345",
            "database_url": "sqlite:///litellm.db"
        }
    }
    
    with open('litellm_config.yaml', 'w') as f:
        import yaml
        yaml.dump(config, f, default_flow_style=False)
    
    print("Created litellm_config.yaml - update with your API keys")
    return config

def provide_solutions():
    """Provide solutions based on the diagnosis"""
    print("\n" + "="*60)
    print("TROUBLESHOOTING SOLUTIONS")
    print("="*60)
    
    print("\n1. LiteLLM Proxy Server Issues:")
    print("   - The configured server (35.175.151.231:8250) is unreachable")
    print("   - Server may be down, misconfigured, or behind a firewall")
    print("   - Network connectivity issues or DNS resolution problems")
    
    print("\n2. Immediate Solutions:")
    print("   a) Use Direct Provider APIs:")
    print("      - Set OPENAI_API_KEY environment variable")
    print("      - Set ANTHROPIC_API_KEY environment variable")
    print("      - Update config to use direct providers instead of proxy")
    
    print("\n   b) Set up Local LiteLLM Proxy:")
    print("      - Install: pip install 'litellm[proxy]'")
    print("      - Create config file with your API keys")
    print("      - Run: litellm --config litellm_config.yaml --port 8250")
    
    print("\n   c) Update Configuration:")
    print("      - Use working LiteLLM proxy endpoint if available")
    print("      - Configure fallback to direct API calls")
    print("      - Implement retry logic with multiple endpoints")
    
    print("\n3. Configuration Updates Needed:")
    print("   - Update llm_config_example.json with working endpoints")
    print("   - Add API keys for direct provider access")
    print("   - Enable fallback_to_rule_based: true")
    
    print("\n4. Code Fixes:")
    print("   - Reduce timeout values for faster fallback")
    print("   - Add more robust error handling")
    print("   - Implement provider rotation logic")

def main():
    """Main troubleshooting function"""
    print("🔍 LiteLLM Connection Troubleshooting")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Test proxy endpoints
    print("1. Testing LiteLLM Proxy Endpoints...")
    proxy_results = test_litellm_proxy_endpoints()
    
    # Test alternative providers
    print("2. Testing Alternative LLM Providers...")
    working_provider, working_model, working_key = test_alternative_providers()
    
    # Create local config
    print("\n3. Creating Local Configuration Template...")
    try:
        create_local_litellm_config()
    except ImportError:
        print("   ❌ PyYAML not installed - run: pip install pyyaml")
    
    # Provide solutions
    provide_solutions()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY")
    print("="*60)
    
    working_endpoints = [url for url, result in proxy_results.items() if result.get('success')]
    
    if working_endpoints:
        print(f"✅ Working endpoints found: {len(working_endpoints)}")
        for endpoint in working_endpoints:
            print(f"   - {endpoint}")
    else:
        print("❌ No working LiteLLM proxy endpoints found")
    
    if working_provider:
        print(f"✅ Working provider found: {working_provider} ({working_model})")
        print("   Recommendation: Use direct API calls instead of proxy")
    else:
        print("❌ No working direct providers found")
        print("   Recommendation: Set up API keys for OpenAI or Anthropic")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Set up API keys for direct provider access")
    print(f"   2. Update configuration to use working endpoints")
    print(f"   3. Test with updated configuration")
    print(f"   4. Consider setting up local LiteLLM proxy")

if __name__ == "__main__":
    main()

