#!/usr/bin/env python3
"""
AWS Athena Connection Test
Quick test to verify AWS Athena setup is working
"""

import json
import boto3
from pathlib import Path
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def load_config():
    """Load Athena configuration"""
    config_path = Path(__file__).parent / "athena_config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Configuration file not found. Run setup_aws_athena.py first")
        return None
    except json.JSONDecodeError:
        print("Invalid configuration file")
        return None

def test_aws_credentials():
    """Test basic AWS credentials"""
    try:
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        print(f"AWS Credentials working")
        print(f"   Account: {response.get('Account', 'Unknown')}")
        print(f"   User/Role: {response.get('Arn', 'Unknown')}")
        return True
    except NoCredentialsError:
        print("No AWS credentials found")
        print("   Run: aws configure")
        return False
    except ClientError as e:
        print(f"AWS credentials error: {e}")
        return False

def test_s3_bucket(config):
    """Test S3 bucket access"""
    try:
        s3 = boto3.client('s3', region_name=config['aws_config']['region'])
        bucket_name = config['aws_config']['results_bucket']

        # Check if bucket exists and is accessible
        s3.head_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' accessible")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"S3 bucket '{bucket_name}' not found")
        elif error_code == '403':
            print(f"No permission to access S3 bucket '{bucket_name}'")
        else:
            print(f"S3 error: {e}")
        return False

def test_athena_access(config):
    """Test Athena service access"""
    try:
        athena = boto3.client('athena', region_name=config['aws_config']['region'])

        # List databases
        response = athena.list_databases(CatalogName='AwsDataCatalog')
        databases = [db['Name'] for db in response['DatabaseList']]
        print(f"Athena accessible")
        print(f"   Available databases: {', '.join(databases[:5])}{'...' if len(databases) > 5 else ''}")

        # Check for Common Crawl
        if 'ccindex' in databases:
            print("Common Crawl database found")
        else:
            print("WARNING: Common Crawl database not found (this is optional)")

        return True
    except ClientError as e:
        print(f"Athena access error: {e}")
        return False

def test_query_execution(config):
    """Test running a simple query"""
    try:
        athena = boto3.client('athena', region_name=config['aws_config']['region'])

        # Simple test query
        test_query = "SELECT 1 as test_column"

        response = athena.start_query_execution(
            QueryString=test_query,
            QueryExecutionContext={'Database': config['aws_config']['database']},
            ResultConfiguration={
                'OutputLocation': config['aws_config']['results_path']
            }
        )

        query_id = response['QueryExecutionId']
        print(f"Test query executed successfully")
        print(f"   Query ID: {query_id}")

        # Check query status
        status_response = athena.get_query_execution(QueryExecutionId=query_id)
        status = status_response['QueryExecution']['Status']['State']
        print(f"   Status: {status}")

        return True
    except ClientError as e:
        print(f"Query execution failed: {e}")
        return False

def main():
    print("AWS Athena Connection Test")
    print("=" * 40)

    # Load configuration
    config = load_config()
    if not config:
        return 1

    print(f"Region: {config['aws_config']['region']}")
    print(f"Bucket: {config['aws_config']['results_bucket']}")
    print()

    # Run tests
    tests = [
        ("AWS Credentials", test_aws_credentials, None),
        ("S3 Bucket Access", test_s3_bucket, config),
        ("Athena Service", test_athena_access, config),
        ("Query Execution", test_query_execution, config)
    ]

    results = []
    for test_name, test_func, test_config in tests:
        print(f"Testing {test_name}...")
        if test_config:
            result = test_func(test_config)
        else:
            result = test_func()
        results.append(result)
        print()

    # Summary
    print("=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)

    passed = sum(results)
    total = len(results)

    for i, (test_name, _, _) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed! AWS Athena is ready to use.")
        print("\nNext steps:")
        print("1. Run: python athena_production_harvester.py")
        print("2. Execute searches and verification")
    else:
        print("\nSome tests failed. Please check the errors above.")
        print("Common solutions:")
        print("1. Run: aws configure")
        print("2. Create S3 bucket with correct name")
        print("3. Check AWS permissions")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
