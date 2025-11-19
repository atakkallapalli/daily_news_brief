#!/usr/bin/env python3
"""
Test script for SF Fed Executive Daily News Digest Generator
"""

from sf_fed_digest_generator import SFFedDigestGenerator
from datetime import datetime

def test_sf_fed_digest():
    """Test the SF Fed digest generation"""
    print("Testing SF Fed Executive Daily News Digest Generator...")
    
    # Initialize generator
    generator = SFFedDigestGenerator(llm_provider="auto")
    
    # Generate digest for today
    print("Generating digest...")
    digest_content = generator.generate_digest()
    
    # Save digest
    filepath = generator.save_digest(digest_content)
    
    print(f"SF Fed Executive Digest saved to: {filepath}")
    print("\n" + "="*80)
    print("SF FED EXECUTIVE DAILY NEWS DIGEST")
    print("="*80)
    print(digest_content)

if __name__ == "__main__":
    test_sf_fed_digest()