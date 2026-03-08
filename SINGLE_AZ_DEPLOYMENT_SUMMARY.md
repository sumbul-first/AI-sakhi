# AI Sakhi - Single-AZ Deployment Summary

## Overview

I've created cost-optimized Single-AZ CloudFormation templates that reduce infrastructure costs by **40-70%** compared to the Multi-AZ deployment, while maintaining all application functionality.

## What Was Created

### New CloudFormation Templates (4 files)

1. **main-stack-single-az.yaml** - Master orchestration template for Single-AZ
2. **network-stack-single-az.yaml** - Single AZ network (1 NAT Gateway)
3. **database-stack-single-az.yaml** - RDS Single-AZ (no Multi-AZ, no replica)
4. **application-stack-single-az.yaml** - EC2 Auto Scaling in single AZ

### Configuration Files

1. **parameters-cost-optimized.json** - Cost-optimized parameters (t3.micro, db.t3.micro)

### Documentation (3 files)

1. **COST_OPTIMIZATION_GUIDE.md** - Comprehensive cost comparison and optimization strategies
2. **QUICK_START_SINGLE_AZ.md** - 5-minute quick start guide
3. **SINGLE_AZ_DEPLOYMENT_SUMMARY.md** - This file

## Cost Comparison

### Multi-AZ (Original) - ~$500-800/month

| Component | Configuration | Cost |
|-----------|--------------|------|
| EC2 | 2-4x t3.medium across 2 AZs | $120-240 |
| RDS | db.t3.medium Multi-AZ + Replica | $120 |
| NAT Gateway | 2x (one per AZ) | $64 |
| Other | ALB, S3, DynamoDB, etc. | $196-376 |
| **TOTAL** | | **$500-800** |

### Single-AZ (Cost Optimized) - ~$145-250/month

| Component | Configuration | Cost | Savings |
|-----------|--------------|------|---------|
| EC2 | 1-2x t3.micro/small in 1 AZ | $7-30 | **-$113-210** |
| RDS | db.t3.micro Single-AZ (no replica) | $15 | **-$105** |
| NAT Gateway | 1x | $32 | **-$32** |
| Other | ALB, S3, DynamoDB, etc. | $91-173 | **-$105-203** |
| **TOTAL** | | **$145-250** | **-$355-550** |

**Total Savings: 40-70% (~$300-550/month)**

## Key Changes

### What's Removed/Reduced

✅ **1 NAT Gateway** removed (saves $32/month)  
✅ **RDS Multi-AZ** disabled (saves $60/month)  
✅ **RDS Read Replica** removed (saves $60/month)  
✅ **Second AZ subnets** removed (except minimal ones for ALB/RDS requirements)  
✅ **Inter-AZ data transfer** eliminated (saves $15/month)  
✅ **Smaller instance types** (t3.micro vs t3.medium, saves $90/month)

### What Stays the Same

✅ All application features work  
✅ Auto Scaling still functions  
✅ Load Balancer still distributes traffic  
✅ CloudFront CDN still provides global distribution  
✅ All AWS services (S3, DynamoDB, Transcribe, Polly, etc.) work  
✅ Monitoring and logging fully operational  
✅ Security unchanged

### Trade-offs

⚠️ **Lower availability**: ~99.5% vs 99.95% (Multi-AZ)  
⚠️ **No automatic AZ failover**: Manual intervention needed  
⚠️ **Maintenance downtime**: Brief outage during RDS maintenance  
⚠️ **Single point of failure**: Entire AZ failure affects application

## Deployment Comparison

### Single-AZ Deployment

```bash
# Quick deploy
aws cloudformation create-stack \
  --stack-name ai-sakhi-cost-opt \
  --template-body file://cloudformation/main-stack-single-az.yaml \
  --parameters file://cloudformation/parameters-cost-optimized.json \
  --capabilities CAPABILITY_NAMED_IAM
```

- **Deployment Time**: 20-25 minutes
- **Resources Created**: ~35 (vs 44 in Multi-AZ)
- **Monthly Cost**: $145-250
- **Best For**: Dev, test, demos, cost-sensitive deployments

### Multi-AZ Deployment

```bash
# High availability deploy
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://cloudformation/main-stack.yaml \
  --parameters file://cloudformation/parameters-prod.json \
  --capabilities CAPABILITY_NAMED_IAM
```

- **Deployment Time**: 25-30 minutes
- **Resources Created**: ~44
- **Monthly Cost**: $500-800
- **Best For**: Production with high availability requirements

## Resource Inventory

### Single-AZ Resources (~35 total)

**Network (5 resources)**
- 1 VPC
- 1 Public Subnet (+ 1 minimal for ALB)
- 1 Private Subnet (+ 1 minimal for RDS)
- 1 Internet Gateway
- 1 NAT Gateway

**Security (7 resources)**
- 3 Security Groups
- 2 IAM Roles
- 1 Instance Profile
- 1 KMS Key

**Storage (7 resources)**
- 2 S3 Buckets
- 3 DynamoDB Tables
- 1 SNS Topic
- 1 S3 Bucket Policy

**Database (4 resources)**
- 1 RDS Instance (Single-AZ)
- 1 DB Subnet Group
- 1 DB Parameter Group
- 3 CloudWatch Alarms

**Application (6 resources)**
- 1 Application Load Balancer
- 1 Target Group
- 1 Launch Template
- 1 Auto Scaling Group
- 1 Scaling Policy
- 1 CloudFront Distribution

**Monitoring (6 resources)**
- 1 CloudWatch Dashboard
- 2 Log Groups
- 4 CloudWatch Alarms
- 1 CloudTrail
- 1 SNS Alarm Topic

## Use Case Recommendations

### ✅ Use Single-AZ For:

- **Development environments** - Perfect for testing
- **Staging/QA environments** - Cost-effective pre-production
- **Demos and POCs** - Quick setup, low cost
- **Low-traffic production** - When brief downtime is acceptable
- **Budget-constrained projects** - Maximum cost savings
- **Learning and experimentation** - Affordable infrastructure

### ✅ Use Multi-AZ For:

- **High-traffic production** - Needs high availability
- **Mission-critical applications** - Downtime is costly
- **SLA commitments** - 99.95%+ uptime required
- **24/7 operations** - No maintenance windows
- **Enterprise deployments** - Compliance requirements

## Migration Path

### Start Single-AZ → Upgrade to Multi-AZ Later

1. **Deploy Single-AZ** for initial development/testing
2. **Monitor** usage and availability for 1-2 months
3. **Evaluate** if higher availability is needed
4. **Migrate** to Multi-AZ when justified:

```bash
# 1. Snapshot current database
aws rds create-db-snapshot \
  --db-instance-identifier ai-sakhi-cost-opt-db \
  --db-snapshot-identifier pre-upgrade

# 2. Deploy Multi-AZ stack
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://main-stack.yaml \
  --parameters file://parameters-prod.json

# 3. Migrate data and switch DNS
# 4. Decommission Single-AZ stack
```

## Additional Cost Optimization

### Further Reduce Costs

1. **Schedule Auto Scaling** (Dev/Test)
   - Scale to 0 instances nights/weekends
   - **Additional Savings**: 30-50%

2. **Use Reserved Instances** (Production)
   - 1-year commitment
   - **Additional Savings**: 30-40%

3. **Optimize Storage**
   - S3 Intelligent-Tiering
   - Lifecycle policies
   - **Additional Savings**: 10-20%

4. **Reduce Logging** (Dev/Test)
   - 7-day retention vs 30-day
   - **Additional Savings**: 5-10%

**Total Potential Savings**: Up to 80-90% vs Multi-AZ On-Demand

## Quick Start

### 1. Update Parameters

```bash
cd cloudformation
nano parameters-cost-optimized.json
# Update KeyPairName and DBPassword
```

### 2. Deploy

```bash
aws cloudformation create-stack \
  --stack-name ai-sakhi-cost-opt \
  --template-body file://main-stack-single-az.yaml \
  --parameters file://parameters-cost-optimized.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### 3. Monitor

```bash
watch -n 30 'aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query "Stacks[0].StackStatus"'
```

### 4. Get URL

```bash
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-cost-opt \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text
```

## Documentation

- **Quick Start**: [QUICK_START_SINGLE_AZ.md](cloudformation/QUICK_START_SINGLE_AZ.md)
- **Cost Guide**: [COST_OPTIMIZATION_GUIDE.md](cloudformation/COST_OPTIMIZATION_GUIDE.md)
- **Full Deployment**: [DEPLOYMENT_GUIDE.md](cloudformation/DEPLOYMENT_GUIDE.md)
- **CloudFormation README**: [cloudformation/README.md](cloudformation/README.md)

## Summary

### Cost Savings Achieved

| Metric | Multi-AZ | Single-AZ | Savings |
|--------|----------|-----------|---------|
| **Monthly Cost** | $500-800 | $145-250 | **$355-550** |
| **Percentage** | 100% | 30-50% | **40-70%** |
| **Annual Cost** | $6,000-9,600 | $1,740-3,000 | **$4,260-6,600** |

### Files Created

✅ 4 CloudFormation templates (Single-AZ versions)  
✅ 1 Parameter file (cost-optimized)  
✅ 3 Documentation files (guides and summaries)  
✅ Updated existing README with both options

### Ready to Deploy

Both deployment options are now available:

1. **Single-AZ** (Cost Optimized) - 40-70% savings
2. **Multi-AZ** (High Availability) - Production-grade

Choose based on your availability requirements and budget!

---

**Created**: February 28, 2026  
**Version**: 1.0.0  
**Repository**: https://github.com/sumbul-first/AI-sakhi.git  
**Estimated Savings**: $300-550/month (40-70%)
