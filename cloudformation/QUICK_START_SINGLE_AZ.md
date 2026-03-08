# AI Sakhi - Single-AZ Quick Start Guide

## 🚀 Deploy Cost-Optimized Infrastructure in 5 Minutes

This guide helps you deploy the AI Sakhi application infrastructure in a single Availability Zone for **40-70% cost savings** compared to Multi-AZ deployment.

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- EC2 Key Pair created
- 5-10 minutes

## Quick Deploy

### Step 1: Update Parameters

Edit `parameters-cost-optimized.json`:

```json
{
  "ParameterKey": "KeyPairName",
  "ParameterValue": "YOUR-KEY-PAIR-NAME"  // ← Change this
},
{
  "ParameterKey": "DBPassword",
  "ParameterValue": "YOUR-SECURE-PASSWORD"  // ← Change this (min 8 chars)
}
```

### Step 2: Deploy Stack

```bash
cd cloudformation

aws cloudformation create-stack \
  --stack-name ai-sakhi-cost-opt \
  --template-body file://main-stack-single-az.yaml \
  --parameters file://parameters-cost-optimized.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 3: Monitor Deployment

```bash
# Watch stack creation (takes ~20-25 minutes)
watch -n 30 'aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query "Stacks[0].StackStatus" \
  --output text'
```

### Step 4: Get Application URL

```bash
# Once status is CREATE_COMPLETE
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text
```

### Step 5: Test Application

```bash
# Get the URL from step 4
curl http://<alb-url>/health
```

## What Gets Deployed

### Infrastructure (Single AZ)
- ✅ 1 VPC with public and private subnets
- ✅ 1 NAT Gateway (saves $32/month vs 2)
- ✅ 1 EC2 instance (t3.micro) with Auto Scaling
- ✅ 1 RDS PostgreSQL (db.t3.micro, Single-AZ)
- ✅ Application Load Balancer
- ✅ CloudFront CDN
- ✅ S3 buckets for content
- ✅ DynamoDB tables for sessions
- ✅ CloudWatch monitoring

### Monthly Cost Estimate
- **Minimum**: ~$145/month (1 instance, minimal usage)
- **Typical**: ~$175/month (1-2 instances, moderate usage)
- **Maximum**: ~$250/month (2 instances, high usage)

**Savings vs Multi-AZ**: 40-70% (~$300-450/month)

## Cost Breakdown

| Service | Cost/Month | Notes |
|---------|-----------|-------|
| EC2 (t3.micro) | $7-15 | 1-2 instances |
| RDS (db.t3.micro) | $15 | Single-AZ |
| NAT Gateway | $32 | 1 gateway |
| ALB | $25 | Load balancer |
| S3 | $3 | 100GB storage |
| DynamoDB | $10 | On-demand |
| CloudFront | $10 | 100GB transfer |
| Data Transfer | $5 | Minimal |
| CloudWatch | $10 | Logs + metrics |
| Other | $5 | SNS, CloudTrail |
| **TOTAL** | **~$122-145** | |

## What's Different from Multi-AZ

### Cost Savings
- ✅ 1 NAT Gateway instead of 2 (-$32/month)
- ✅ RDS Single-AZ instead of Multi-AZ (-$60/month)
- ✅ No Read Replica (-$60/month)
- ✅ Smaller instances (-$90/month)
- ✅ No inter-AZ data transfer (-$15/month)

### Trade-offs
- ⚠️ Lower availability (~99.5% vs 99.95%)
- ⚠️ No automatic AZ failover
- ⚠️ Brief downtime during RDS maintenance
- ⚠️ Single point of failure at AZ level

### What Stays the Same
- ✅ All application features work
- ✅ Auto Scaling still functions
- ✅ Load balancing still works
- ✅ Monitoring fully operational
- ✅ Security unchanged

## Post-Deployment

### 1. Deploy Application Code

```bash
# Package application
zip -r ai-sakhi-app.zip . -x "*.git*" -x "*__pycache__*"

# Upload to S3
aws s3 cp ai-sakhi-app.zip s3://ai-sakhi-content-cost-opt-<account-id>/app/
```

### 2. Initialize Database

```bash
# Get DB endpoint
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' \
  --output text)

# Connect and initialize (from EC2 instance)
psql -h $DB_ENDPOINT -U aisakhi_admin -d aisakhi -f database/schema.sql
```

### 3. Set Up Billing Alert

```bash
# Create billing alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ai-sakhi-cost-alert \
  --alarm-description "Alert when monthly cost exceeds $200" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 200 \
  --comparison-operator GreaterThanThreshold
```

## Scaling Options

### Scale Up (More Capacity)

```bash
# Increase instance count
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name ai-sakhi-cost-opt-asg \
  --min-size 1 \
  --max-size 3 \
  --desired-capacity 2
```

### Scale Down (Save Costs)

```bash
# Reduce to single instance
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name ai-sakhi-cost-opt-asg \
  --min-size 1 \
  --max-size 1 \
  --desired-capacity 1
```

### Schedule Scaling (Dev/Test)

```bash
# Scale down at night (10 PM)
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name ai-sakhi-cost-opt-asg \
  --scheduled-action-name scale-down-night \
  --recurrence "0 22 * * *" \
  --min-size 0 \
  --max-size 0 \
  --desired-capacity 0

# Scale up in morning (8 AM)
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name ai-sakhi-cost-opt-asg \
  --scheduled-action-name scale-up-morning \
  --recurrence "0 8 * * *" \
  --min-size 1 \
  --max-size 2 \
  --desired-capacity 1
```

## Monitoring

### View CloudWatch Dashboard

```bash
# Get dashboard URL
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudWatchDashboardURL`].OutputValue' \
  --output text
```

### Check Application Logs

```bash
# Tail application logs
aws logs tail /aws/ec2/ai-sakhi-cost-opt/application --follow
```

### Check Costs

```bash
# View current month costs
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

## Troubleshooting

### Stack Creation Failed

```bash
# Check events
aws cloudformation describe-stack-events \
  --stack-name ai-sakhi-cost-opt \
  --max-items 20
```

### Application Not Accessible

```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws cloudformation describe-stacks \
    --stack-name ai-sakhi-cost-opt \
    --query 'Stacks[0].Outputs[?OutputKey==`TargetGroupArn`].OutputValue' \
    --output text)
```

### Database Connection Issues

```bash
# Test from EC2 instance
ssh -i your-key.pem ec2-user@<instance-ip>
psql -h <db-endpoint> -U aisakhi_admin -d aisakhi
```

## Cleanup

### Delete Everything

```bash
# Delete stack (removes all resources)
aws cloudformation delete-stack --stack-name ai-sakhi-cost-opt

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name ai-sakhi-cost-opt

# Manually empty and delete S3 buckets
aws s3 rm s3://ai-sakhi-content-cost-opt-<account-id> --recursive
aws s3 rb s3://ai-sakhi-content-cost-opt-<account-id>
```

## Upgrade to Multi-AZ

When you need higher availability:

```bash
# 1. Create snapshot of current database
aws rds create-db-snapshot \
  --db-instance-identifier ai-sakhi-cost-opt-db \
  --db-snapshot-identifier pre-upgrade-snapshot

# 2. Deploy Multi-AZ stack
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://main-stack.yaml \
  --parameters file://parameters-prod.json \
  --capabilities CAPABILITY_NAMED_IAM

# 3. Migrate data and DNS
# 4. Delete old Single-AZ stack
```

## Next Steps

1. ✅ Deploy application code
2. ✅ Initialize database schema
3. ✅ Upload content to S3
4. ✅ Configure DNS (optional)
5. ✅ Set up SSL/TLS (optional)
6. ✅ Configure monitoring alerts
7. ✅ Test all features
8. ✅ Monitor costs

## Support

- **Cost Optimization Guide**: See `COST_OPTIMIZATION_GUIDE.md`
- **Full Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **Architecture Details**: See `../AI-SAKHI-ARCHITECTURE-SUMMARY.md`

---

**Estimated Deployment Time**: 20-25 minutes  
**Estimated Monthly Cost**: $145-250  
**Cost Savings vs Multi-AZ**: 40-70% (~$300-450/month)

**Perfect For**: Development, testing, demos, cost-sensitive deployments
