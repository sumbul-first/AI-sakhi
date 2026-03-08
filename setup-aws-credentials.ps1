# AI Sakhi - AWS Credentials Setup Script
# This script helps you configure AWS credentials for Kiro

Write-Host "=== AI Sakhi - AWS Credentials Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is installed
Write-Host "Checking AWS CLI installation..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version 2>&1
    Write-Host "✓ AWS CLI is installed: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install AWS CLI from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    Write-Host "Or run: winget install Amazon.AWSCLI" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Choose configuration method:" -ForegroundColor Cyan
Write-Host "1. Configure AWS CLI (Recommended)"
Write-Host "2. Set Environment Variables (Temporary)"
Write-Host "3. Check Current Configuration"
Write-Host "4. Exit"
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Configuring AWS CLI..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You'll need:" -ForegroundColor Cyan
        Write-Host "  - AWS Access Key ID"
        Write-Host "  - AWS Secret Access Key"
        Write-Host "  - Default region (e.g., us-east-1)"
        Write-Host ""
        Write-Host "Get credentials from: AWS Console → IAM → Security Credentials → Access Keys" -ForegroundColor Yellow
        Write-Host ""
        
        aws configure
        
        Write-Host ""
        Write-Host "Testing connection..." -ForegroundColor Yellow
        try {
            $identity = aws sts get-caller-identity 2>&1
            Write-Host "✓ Successfully connected to AWS!" -ForegroundColor Green
            Write-Host $identity
        } catch {
            Write-Host "✗ Failed to connect to AWS" -ForegroundColor Red
            Write-Host "Please check your credentials and try again" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Setting Environment Variables..." -ForegroundColor Yellow
        Write-Host ""
        
        $accessKey = Read-Host "Enter AWS Access Key ID"
        $secretKey = Read-Host "Enter AWS Secret Access Key" -AsSecureString
        $region = Read-Host "Enter AWS Region (default: us-east-1)"
        
        if ([string]::IsNullOrWhiteSpace($region)) {
            $region = "us-east-1"
        }
        
        # Convert SecureString to plain text
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretKey)
        $secretKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        
        # Set environment variables
        $env:AWS_ACCESS_KEY_ID = $accessKey
        $env:AWS_SECRET_ACCESS_KEY = $secretKeyPlain
        $env:AWS_DEFAULT_REGION = $region
        
        Write-Host ""
        Write-Host "✓ Environment variables set for this session" -ForegroundColor Green
        Write-Host ""
        Write-Host "Note: These will be lost when you close PowerShell" -ForegroundColor Yellow
        Write-Host "To make permanent, add to your PowerShell profile or use Option 1" -ForegroundColor Yellow
        
        Write-Host ""
        Write-Host "Testing connection..." -ForegroundColor Yellow
        try {
            $identity = aws sts get-caller-identity 2>&1
            Write-Host "✓ Successfully connected to AWS!" -ForegroundColor Green
            Write-Host $identity
        } catch {
            Write-Host "✗ Failed to connect to AWS" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Checking current AWS configuration..." -ForegroundColor Yellow
        Write-Host ""
        
        # Check credentials file
        $credFile = "$env:USERPROFILE\.aws\credentials"
        if (Test-Path $credFile) {
            Write-Host "✓ Credentials file exists: $credFile" -ForegroundColor Green
        } else {
            Write-Host "✗ Credentials file not found: $credFile" -ForegroundColor Red
        }
        
        # Check config file
        $configFile = "$env:USERPROFILE\.aws\config"
        if (Test-Path $configFile) {
            Write-Host "✓ Config file exists: $configFile" -ForegroundColor Green
        } else {
            Write-Host "✗ Config file not found: $configFile" -ForegroundColor Red
        }
        
        # Check environment variables
        Write-Host ""
        Write-Host "Environment Variables:" -ForegroundColor Cyan
        if ($env:AWS_ACCESS_KEY_ID) {
            Write-Host "  AWS_ACCESS_KEY_ID: Set (hidden)" -ForegroundColor Green
        } else {
            Write-Host "  AWS_ACCESS_KEY_ID: Not set" -ForegroundColor Yellow
        }
        
        if ($env:AWS_SECRET_ACCESS_KEY) {
            Write-Host "  AWS_SECRET_ACCESS_KEY: Set (hidden)" -ForegroundColor Green
        } else {
            Write-Host "  AWS_SECRET_ACCESS_KEY: Not set" -ForegroundColor Yellow
        }
        
        if ($env:AWS_DEFAULT_REGION) {
            Write-Host "  AWS_DEFAULT_REGION: $env:AWS_DEFAULT_REGION" -ForegroundColor Green
        } else {
            Write-Host "  AWS_DEFAULT_REGION: Not set" -ForegroundColor Yellow
        }
        
        # Test connection
        Write-Host ""
        Write-Host "Testing AWS connection..." -ForegroundColor Yellow
        try {
            $identity = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
            Write-Host "✓ Successfully connected to AWS!" -ForegroundColor Green
            Write-Host "  Account: $($identity.Account)" -ForegroundColor Cyan
            Write-Host "  User ARN: $($identity.Arn)" -ForegroundColor Cyan
            Write-Host "  User ID: $($identity.UserId)" -ForegroundColor Cyan
        } catch {
            Write-Host "✗ Not connected to AWS" -ForegroundColor Red
            Write-Host "  Run Option 1 or 2 to configure credentials" -ForegroundColor Yellow
        }
    }
    
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy CloudFormation stack:"
Write-Host "   cd cloudformation"
Write-Host "   aws cloudformation create-stack --stack-name ai-sakhi-cost-opt ..."
Write-Host ""
Write-Host "2. See QUICK_START_SINGLE_AZ.md for deployment instructions"
Write-Host ""
