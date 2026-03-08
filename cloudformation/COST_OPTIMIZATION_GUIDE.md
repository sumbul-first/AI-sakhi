# AI Sakhi - Cost Optimization Guide

## Overview

This guide explains the cost differences between Multi-AZ and Single-AZ deployments and provides recommendations for cost optimization.

## Deployment Options

### Option 1: Multi-AZ Deployment (High Availability)
- **Templates**: `main-stack.yaml` + multi-AZ templates
- **Use Case**: Production environments requiring 99.95%+ uptime
- **Cost**: ~$500-800/month

### Option 2: Single-AZ Deployment (Cost Optimized)
- **Templates**: `main-stack-single-az.yaml` + single-AZ templates
- **Use Case**: Development, testing, or cost-sensitive deployments
- **Cost**: ~$250-400/month (40-50% savings)

## Cost Comparison

### Multi-AZ Deployment (~$500-800/month)

| Service | Configuration | Monthly Cost | Notes |
|---------|--------------|--------------|-------|
| **EC2** | 2-4x t3.medium | $120-240 | Auto Scaling across 2 AZs |
| **RDS** | db.t3.medium Multi-AZ + Replica | $120 | Automatic failover + read scaling |
| **NAT Gateway** | 2x (one per AZ) | $64 | $32 each + data transfer |
| **ALB** | 1x across 2 AZs | $25 | Load balancing |
| **CloudFront** | 500GB transfer | $40 | CDN |
| **S3** | 500GB storage | $12 | Content + static assets |
| **DynamoDB** | On-demand | $30 | Sessions + interactions |
| **Data Transfer** | 200GB | $20 | Inter-AZ + internet |
| **CloudWatch** | Logs + Metrics | $30 | Monitoring |
| **Other** | CloudTrail, SNS, etc. | $10 | Supporting services |
| **TOTAL** | | **$471-631** | |

### Single-AZ Deployment (~$250-400/month)

| Service | Configuration | Monthly Cost | Savings | Notes |
|---------|--------------|--------------|---------|-------|
| **EC2** | 1-2x t3.small | $30-60 | -$90-180 | Single AZ, smaller instances |
| **RDS** | db.t3.micro Single-AZ | $15 | -$105 | No Multi-AZ, no replica |
| **NAT Gateway** | 1x | $32 | -$32 | Single NAT Gateway |
| **ALB** | 1x (min 2 subnets) | $25 | $0 | Required for ALB |
| **CloudFront** | 100GB transfer | $10 | -$30 | Reduced usage |
| **S3** | 100GB storage | $3 | -$9 | Smaller storage |
| **DynamoDB** | On-demand | $10 | -$20 | Lower usage |
| **Data Transfer** | 50GB | $5 | -$15 | No inter-AZ transfer |
| **CloudWatch** | Logs + Metrics | $10 | -$20 | Reduced logging |
| **Other** | CloudTrail, SNS, etc. | $5 | -$5 | Minimal services |
| **TOTAL** | | **$145-175** | **-$326-456** | **~50-70% savings** |

## What Changes in Single-AZ Deployment

### Network Changes
- ✅ **1 NAT Gateway** instead of 2 (saves ~$32/month)
- ✅ **1 Private Subnet** instead of 2
- ✅ **1 Public Subnet** instead of 2 (ALB requires 2, so we create a minimal second one)
- ✅ **No inter-AZ data transfer** costs

### Database Changes
- ✅ **RDS Single-AZ** instead of Multi-AZ (saves ~$60/month)
- ✅ **No Read Replica** (saves ~$60/month)
- ⚠️ **No automatic failover** to another AZ
- ⚠️ **Downtime during maintenance** windows

### Application Changes
- ✅ **Instances in single AZ** (no inter-AZ traffic)
- ✅ **Smaller instance types** (t3.micro/small vs t3.medium)
- ✅ **Fewer instances** (1-2 vs 2-4)
- ⚠️ **No AZ-level redundancy**

### What Stays the Same
- ✅ **Auto Scaling** still works (within single AZ)
- ✅ **Load Balancer** still distributes traffic
- ✅ **CloudFront CDN** still provides global distribution
- ✅ **All application features** remain functional
- ✅ **Monitoring and logging** fully operational

## Trade-offs

### Multi-AZ Advantages
- ✅ **High Availability**: 99.95%+ uptime SLA
- ✅ **Automatic Failover**: RDS fails over to standby in another AZ
- ✅ **AZ Failure Protection**: Survives entire AZ outage
- ✅ **Zero Downtime Maintenance**: RDS maintenance with no downtime
- ✅ **Read Scaling**: Read replica for database scaling

### Single-AZ Advantages
- ✅ **40-70% Cost Savings**: Significantly lower monthly costs
- ✅ **Simpler Architecture**: Easier to understand and manage
- ✅ **Faster Deployment**: Fewer resources to create
- ✅ **Lower Data Transfer Costs**: No inter-AZ charges
- ✅ **Suitable for Dev/Test**: Perfect for non-production environments

### Single-AZ Disadvantages
- ⚠️ **Lower Availability**: ~99.5% uptime (vs 99.95% Multi-AZ)
- ⚠️ **AZ Failure Impact**: Entire application down if AZ fails
- ⚠️ **Maintenance Downtime**: RDS maintenance causes brief outage
- ⚠️ **No Automatic Failover**: Manual intervention needed for failures
- ⚠️ **Single Point of Failure**: AZ-level issues affect entire app

## Deployment Instructions

### Deploy Single-AZ (Cost Optimized)

```bash
# Using AWS CLI
aws cloudformation create-stack \
  --stack-name ai-sakhi-cost-opt \
  --template-body file://cloudformation/main-stack-single-az.yaml \
  --parameters file://cloudformation/parameters-cost-optimized.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Monitor deployment
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query 'Stacks[0].StackStatus'
```

### Deploy Multi-AZ (High Availability)

```bash
# Using AWS CLI
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://cloudformation/main-stack.yaml \
  --parameters file://cloudformation/parameters-prod.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## Additional Cost Optimization Tips

### 1. Use Reserved Instances (Production)
- **Savings**: Up to 72% vs On-Demand
- **Commitment**: 1 or 3 years
- **Best For**: Baseline capacity in production

```bash
# Example: Reserve 1x t3.small for 1 year
# Savings: ~$10-15/month per instance
```

### 2. Use Savings Plans
- **Savings**: Up to 72% vs On-Demand
- **Flexibility**: More flexible than Reserved Instances
- **Best For**: Variable workloads

### 3. Schedule Auto Scaling
- **Savings**: 30-50% for non-24/7 workloads
- **Example**: Scale down to 0 instances nights/weekends

```yaml
# Add to Auto Scaling Group
ScheduledActions:
  - ScheduledActionName: ScaleDownNight
    Recurrence: "0 22 * * *"  # 10 PM daily
    MinSize: 0
    MaxSize: 0
    DesiredCapacity: 0
  - ScheduledActionName: ScaleUpMorning
    Recurrence: "0 8 * * *"   # 8 AM daily
    MinSize: 1
    MaxSize: 2
    DesiredCapacity: 1
```

### 4. Optimize S3 Storage
- **Use S3 Intelligent-Tiering**: Automatic cost optimization
- **Lifecycle Policies**: Move old data to cheaper storage classes
- **Compression**: Compress audio/video files

```yaml
LifecycleConfiguration:
  Rules:
    - Id: MoveToIA
      Status: Enabled
      Transitions:
        - TransitionInDays: 30
          StorageClass: STANDARD_IA
        - TransitionInDays: 90
          StorageClass: GLACIER
```

### 5. Optimize DynamoDB
- **Use On-Demand**: Pay per request (already configured)
- **Enable Auto Scaling**: For provisioned capacity (if switched)
- **TTL**: Automatically delete old data

### 6. Reduce Data Transfer Costs
- **Use VPC Endpoints**: Free for S3 and DynamoDB (already configured)
- **CloudFront**: Reduces origin data transfer costs
- **Compression**: Enable gzip compression

### 7. Optimize CloudWatch
- **Log Retention**: Reduce from 30 to 7 days for dev
- **Metric Resolution**: Use 5-minute instead of 1-minute
- **Filter Logs**: Only log errors in production

### 8. Use Spot Instances (Advanced)
- **Savings**: Up to 90% vs On-Demand
- **Risk**: Can be terminated with 2-minute notice
- **Best For**: Batch processing, non-critical workloads

## Cost Monitoring

### Set Up Billing Alerts

```bash
# Create SNS topic for billing alerts
aws sns create-topic --name billing-alerts

# Subscribe to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Create billing alarm (via CloudWatch)
aws cloudwatch put-metric-alarm \
  --alarm-name monthly-cost-alert \
  --alarm-description "Alert when monthly cost exceeds $200" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 200 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts
```

### Use AWS Cost Explorer
- Enable Cost Explorer in AWS Console
- Set up cost allocation tags
- Create custom cost reports
- Analyze spending trends

### Use AWS Budgets
- Set monthly budget limits
- Get alerts at 80%, 100%, 120% of budget
- Track costs by service

## Recommendations by Use Case

### Development/Testing
- ✅ **Use Single-AZ deployment**
- ✅ **Use t3.micro instances**
- ✅ **Scale to 0 outside work hours**
- ✅ **Use minimal storage**
- **Estimated Cost**: $50-100/month

### Staging/QA
- ✅ **Use Single-AZ deployment**
- ✅ **Use t3.small instances**
- ✅ **Keep running 24/7**
- ✅ **Moderate storage**
- **Estimated Cost**: $150-250/month

### Production (Low Traffic)
- ⚠️ **Consider Single-AZ** if downtime acceptable
- ✅ **Use t3.small instances**
- ✅ **Enable Auto Scaling**
- ✅ **Use Reserved Instances**
- **Estimated Cost**: $200-350/month

### Production (High Traffic)
- ✅ **Use Multi-AZ deployment**
- ✅ **Use t3.medium+ instances**
- ✅ **Enable Auto Scaling**
- ✅ **Use Reserved Instances**
- ✅ **Use CloudFront CDN**
- **Estimated Cost**: $400-800/month

## Migration Path

### Start with Single-AZ, Migrate to Multi-AZ Later

1. **Deploy Single-AZ** for initial launch
2. **Monitor usage** and costs for 1-2 months
3. **Evaluate availability** requirements
4. **Migrate to Multi-AZ** when needed:

```bash
# Export data from Single-AZ
aws rds create-db-snapshot \
  --db-instance-identifier ai-sakhi-cost-opt-db \
  --db-snapshot-identifier pre-migration-snapshot

# Deploy Multi-AZ stack
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://main-stack.yaml \
  --parameters file://parameters-prod.json

# Restore data to Multi-AZ
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-sakhi-prod-db \
  --db-snapshot-identifier pre-migration-snapshot

# Update DNS to point to new stack
# Decommission old Single-AZ stack
```

## Summary

### Choose Single-AZ If:
- ✅ Development or testing environment
- ✅ Cost is primary concern
- ✅ Brief downtime is acceptable
- ✅ Traffic is low to moderate
- ✅ Budget is limited

### Choose Multi-AZ If:
- ✅ Production environment
- ✅ High availability required
- ✅ Downtime is costly
- ✅ Traffic is high
- ✅ SLA commitments exist

### Cost Savings Summary
- **Single-AZ vs Multi-AZ**: 40-70% savings
- **With Reserved Instances**: Additional 30-72% savings
- **With Scheduled Scaling**: Additional 30-50% savings
- **Total Potential Savings**: Up to 80-90% vs Multi-AZ On-Demand

---

**Recommendation**: Start with Single-AZ for development/testing, then migrate to Multi-AZ for production when availability requirements justify the additional cost.

**Created**: February 28, 2026  
**Version**: 1.0.0  
**Repository**: https://github.com/sumbul-first/AI-sakhi.git
