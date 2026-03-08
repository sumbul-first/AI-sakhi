# Diagnose CloudFormation Stack Failure

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   CloudFormation Stack Failure Diagnosis" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Get stack name from user or use default
$stackName = Read-Host "Enter stack name (default: ai-sakhi-dev)"
if ([string]::IsNullOrWhiteSpace($stackName)) {
    $stackName = "ai-sakhi-dev"
}

Write-Host ""
Write-Host "Checking stack: $stackName" -ForegroundColor Yellow
Write-Host ""

# Get stack status
Write-Host "[1/4] Getting stack status..." -ForegroundColor Yellow
try {
    $stackStatus = aws cloudformation describe-stacks --stack-name $stackName --query 'Stacks[0].StackStatus' --output text 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Stack Status: $stackStatus" -ForegroundColor $(if ($stackStatus -like "*FAILED*") { "Red" } else { "Green" })
    } else {
        Write-Host "  ERROR: Could not get stack status" -ForegroundColor Red
        Write-Host "  $stackStatus" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

# Get failed resources
Write-Host ""
Write-Host "[2/4] Finding failed resources..." -ForegroundColor Yellow
try {
    $failedEvents = aws cloudformation describe-stack-events --stack-name $stackName --query 'StackEvents[?ResourceStatus==`CREATE_FAILED` || ResourceStatus==`UPDATE_FAILED`].[Timestamp,LogicalResourceId,ResourceType,ResourceStatusReason]' --output table 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $failedEvents
    } else {
        Write-Host "  ERROR: Could not get failed events" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

# Get nested stack failures
Write-Host ""
Write-Host "[3/4] Checking nested stacks..." -ForegroundColor Yellow
try {
    $nestedStacks = aws cloudformation list-stacks --stack-status-filter CREATE_FAILED UPDATE_FAILED ROLLBACK_COMPLETE --query 'StackSummaries[?contains(StackName, `ai-sakhi`)].[StackName,StackStatus,StackStatusReason]' --output table 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $nestedStacks
    } else {
        Write-Host "  No nested stack failures found" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

# Get recent events
Write-Host ""
Write-Host "[4/4] Recent stack events (last 10)..." -ForegroundColor Yellow
try {
    $recentEvents = aws cloudformation describe-stack-events --stack-name $stackName --max-items 10 --query 'StackEvents[].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' --output table 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $recentEvents
    } else {
        Write-Host "  ERROR: Could not get recent events" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Common Issues and Solutions" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Template URL not accessible:" -ForegroundColor Yellow
Write-Host "   - Check if S3 bucket exists and templates are uploaded" -ForegroundColor Gray
Write-Host "   - Verify bucket name matches pattern in main stack" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Parameter validation failed:" -ForegroundColor Yellow
Write-Host "   - Check KeyPairName exists in your region" -ForegroundColor Gray
Write-Host "   - Verify DBPassword meets requirements (min 8 chars)" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Resource limits exceeded:" -ForegroundColor Yellow
Write-Host "   - Check VPC limit (default: 5 per region)" -ForegroundColor Gray
Write-Host "   - Check Elastic IP limit (default: 5 per region)" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Insufficient permissions:" -ForegroundColor Yellow
Write-Host "   - Verify IAM user has AdministratorAccess" -ForegroundColor Gray
Write-Host "   - Check CloudFormation service role permissions" -ForegroundColor Gray
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the error messages above" -ForegroundColor Gray
Write-Host "2. Fix the identified issues" -ForegroundColor Gray
Write-Host "3. Delete the failed stack: aws cloudformation delete-stack --stack-name $stackName" -ForegroundColor Gray
Write-Host "4. Try deployment again" -ForegroundColor Gray
Write-Host ""
