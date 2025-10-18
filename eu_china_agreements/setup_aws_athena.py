#!/usr/bin/env python3
"""
AWS Athena Setup Guide for EU-China Agreements Discovery
Complete infrastructure setup with step-by-step instructions
"""

import json
import boto3
import sys
from pathlib import Path
from datetime import datetime
import uuid

def print_step(step_num, title, description):
    """Print formatted step information"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")
    print(description)
    print()

def main():
    print("AWS Athena Setup for EU-China Agreements Discovery")
    print("=" * 60)
    print("This script will guide you through setting up AWS Athena infrastructure")
    print("Required: AWS account, AWS CLI installed, basic permissions")
    print()

    # Step 1: Check AWS CLI
    print_step(1, "Check AWS CLI Installation",
        "First, let's verify AWS CLI is installed and working")

    print("Run this command to check AWS CLI:")
    print("aws --version")
    print()

    response = input("Is AWS CLI installed? (y/n): ").lower()
    if response != 'y':
        print("\n❌ Please install AWS CLI first:")
        print("1. Download from: https://aws.amazon.com/cli/")
        print("2. Follow installation instructions for your OS")
        print("3. Run this script again")
        return

    # Step 2: AWS Credentials
    print_step(2, "Configure AWS Credentials",
        "We'll set up AWS credentials for accessing Athena")

    print("Choose your authentication method:")
    print("1. AWS CLI configure (recommended for personal use)")
    print("2. IAM Role (for EC2/Lambda)")
    print("3. Environment variables")
    print()

    auth_method = input("Enter choice (1-3): ").strip()

    if auth_method == "1":
        print("\n📋 You'll need:")
        print("- AWS Access Key ID")
        print("- AWS Secret Access Key")
        print("- Default region (us-east-1)")
        print()
        print("Run this command to configure:")
        print("aws configure")
        print()
        print("When prompted:")
        print("- Access Key ID: [Your Access Key]")
        print("- Secret Access Key: [Your Secret Key]")
        print("- Default region: us-east-1")
        print("- Default output format: json")
        print()

        configured = input("Have you run 'aws configure'? (y/n): ").lower()
        if configured != 'y':
            print("Please run 'aws configure' first, then restart this script")
            return

    elif auth_method == "2":
        print("\n📋 Using IAM Role:")
        print("- Ensure your EC2/Lambda has appropriate IAM role")
        print("- Role should have AthenaFullAccess and S3 permissions")

    else:
        print("\n📋 Using Environment Variables:")
        print("Set these environment variables:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("export AWS_DEFAULT_REGION=us-east-1")

    # Step 3: Test AWS Connection
    print_step(3, "Test AWS Connection",
        "Let's verify your AWS credentials work")

    print("Run this command to test:")
    print("aws sts get-caller-identity")
    print()

    works = input("Did the command show your AWS account info? (y/n): ").lower()
    if works != 'y':
        print("❌ AWS credentials not working. Please check:")
        print("1. Access keys are correct")
        print("2. Region is set to us-east-1")
        print("3. Account has necessary permissions")
        return

    # Step 4: Create S3 Bucket
    print_step(4, "Create S3 Bucket for Query Results",
        "Athena needs an S3 bucket to store query results")

    bucket_name = f"athena-eu-china-results-{uuid.uuid4().hex[:8]}"
    print(f"We'll create bucket: {bucket_name}")
    print()

    print("Run this command to create the bucket:")
    print(f"aws s3 mb s3://{bucket_name} --region us-east-1")
    print()

    bucket_created = input("Did the bucket create successfully? (y/n): ").lower()
    if bucket_created != 'y':
        print("❌ Bucket creation failed. Common issues:")
        print("1. Bucket name already exists (try different name)")
        print("2. Insufficient S3 permissions")
        print("3. Region mismatch")
        return

    bucket_name_actual = input(f"Enter the bucket name you created (or press Enter for {bucket_name}): ").strip()
    if bucket_name_actual:
        bucket_name = bucket_name_actual

    # Step 5: Set up Athena
    print_step(5, "Configure Athena",
        "Set up Athena workgroup and query result location")

    print("Run this command to set query result location:")
    print(f"aws athena put-work-group --work-group primary --configuration-updates 'ResultConfigurationUpdates={{OutputLocation=s3://{bucket_name}/query-results/}}'")
    print()

    athena_configured = input("Did Athena configuration succeed? (y/n): ").lower()
    if athena_configured != 'y':
        print("❌ Athena configuration failed. Check:")
        print("1. You have Athena permissions")
        print("2. Bucket name is correct")
        print("3. Region is us-east-1")
        return

    # Step 6: Test Common Crawl Access
    print_step(6, "Test Common Crawl Database Access",
        "Verify you can access the Common Crawl dataset")

    print("Run this command to list Common Crawl databases:")
    print("aws athena list-databases --catalog-name AwsDataCatalog")
    print()

    cc_access = input("Do you see 'ccindex' in the database list? (y/n): ").lower()
    if cc_access != 'y':
        print("⚠️  Common Crawl access may be limited, but we can proceed")
        print("You may need to set up Common Crawl access separately")

    # Step 7: Update Configuration
    print_step(7, "Update Configuration File",
        "Now we'll update the Athena configuration with your settings")

    config = {
        "aws_config": {
            "region": "us-east-1",
            "database": "default",
            "results_bucket": bucket_name,
            "results_path": f"s3://{bucket_name}/query-results/",
            "profile": "default" if auth_method == "1" else None
        },
        "common_crawl": {
            "table": "ccindex",
            "database": "ccindex",
            "latest_crawl": "CC-MAIN-2024-10",
            "crawl_history": [
                "CC-MAIN-2024-10",
                "CC-MAIN-2024-18",
                "CC-MAIN-2024-22",
                "CC-MAIN-2024-26"
            ]
        },
        "search_templates": {
            "sister_cities": {
                "keywords": ["sister city", "sister cities", "jumelage", "städtepartnerschaft", "gemellaggio"],
                "china_terms": ["china", "chinese", "beijing", "shanghai", "guangzhou", "chine", "chinois"]
            },
            "academic_partnerships": {
                "keywords": ["university partnership", "research collaboration", "academic exchange", "cooperation agreement"],
                "china_terms": ["china", "chinese", "tsinghua", "peking university", "fudan", "jiaotong"]
            },
            "government_agreements": {
                "keywords": ["memorandum understanding", "cooperation agreement", "bilateral agreement", "partnership protocol"],
                "china_terms": ["china", "chinese", "people's republic", "prc"]
            }
        },
        "verification_settings": {
            "max_results_per_query": 1000,
            "timeout_seconds": 300,
            "retry_attempts": 3
        }
    }

    config_path = Path(__file__).parent / "athena_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved to: {config_path}")

    # Step 8: Test the Setup
    print_step(8, "Test Complete Setup",
        "Let's test the Athena harvester with your configuration")

    print("Run this command to test:")
    print("python athena_production_harvester.py --test-connection")
    print()

    test_works = input("Did the connection test pass? (y/n): ").lower()
    if test_works == 'y':
        print("SUCCESS! Your AWS Athena setup is complete")
        print()
        print("Next Steps:")
        print("1. Run the harvester: python athena_production_harvester.py")
        print("2. Execute EUR-Lex searches: python official_database_searcher.py")
        print("3. Verify partnerships: python automated_verification_processor.py")

    else:
        print("Test failed. Check the error messages and:")
        print("1. Verify all AWS commands worked")
        print("2. Check bucket permissions")
        print("3. Ensure region is us-east-1")
        print("4. Review AWS credentials")

    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    print(f"Region: us-east-1")
    print(f"S3 Bucket: {bucket_name}")
    print(f"Query Results: s3://{bucket_name}/query-results/")
    print(f"Config File: {config_path}")
    print()
    print("Useful Links:")
    print("- AWS Athena Console: https://console.aws.amazon.com/athena/")
    print(f"- S3 Bucket: https://console.aws.amazon.com/s3/buckets/{bucket_name}")
    print("- Common Crawl: https://commoncrawl.org/")
    print()
    print("Save this information for future reference!")

if __name__ == "__main__":
    main()
