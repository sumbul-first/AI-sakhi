# AI Sakhi - CloudFormation Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the AI Sakhi application infrastructure on AWS using CloudFormation templates.

## Architecture Components

The deployment creates the following AWS resources:

### Network Layer
- VPC with public and private subnets across 2 Availability Zones
- Internet Gateway for public internet access
- NAT Gateways for private subnet internet access
- Route tables and VPC endpoints (S3, DynamoDB)

### Security Layer
- Security Groups (ALB, EC2, RDS)
- IAM Roles and Policies
- KMS encryption keys

### Storage Layer
- S3 buckets (content storage, static assets)
- DynamoDB tables (sessions, interactions, reminders)
- SNS topics for notifications

### Database Layer
- RDS PostgreSQL (Multi-AZ)
- Read replica for scaling
- Automated backups and monitoring

### Application Layer
- EC2 instances with Auto Scaling
- Application Load Balancer
- CloudFront CDN
- Launch templates with user data

### Monitoring Layer
- CloudWatch dashboards and alarms
- CloudTrail for audit logging
- Enhanced monitoring for RDS

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **EC2 Key Pair** created in your target region
4. **S3 Bucket** for CloudFormation templates (optional but recommended)
5. **Database Password** (minimum 8 characters)

## Deployment Steps

### Step 1: Prepare CloudFormation Templates

Upload all CloudFormation templates to an S3 bucket:

```bash
# Create S3 bucket for templates
aws s3 mb s3://ai-sakhi-cfn-templates-<your-account-id>

# Upload templates
aws s3 cp cloudformation/ s3://ai-sakhi-cfn-templates-<your-account-id>/cloudformation/ --recursive
```

### Step 2: Update Main Stack Template

Edit `main-stack.yaml` and update the `TemplateURL` parameters to point to your S3 bucket:

```yaml
TemplateURL: !Sub 'https://s3.amazonaws.com/ai-sakhi-cfn-templates-${AWS::AccountId}/cloudformation/network-stack.yaml'
```

### Step 3: Deploy the Stack

#### Option A: Using AWS Console

1. Navigate to CloudFormation in AWS Console
2. Click "Create Stack" → "With new resources"
3. Upload `main-stack.yaml` template
4. Fill in parameters:
   - **EnvironmentName**: `ai-sakhi-prod`
   - **EnvironmentType**: `production`
   - **KeyPairName**: Your EC2 key pair name
   - **DBPassword**: Strong database password
   - **ContentBucketName**: `ai-sakhi-content`
5. Review and create stack

#### Option B: Using AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name ai-sakhi-main \
  --template-body file://cloudformation/main-stack.yaml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=ai-sakhi-prod \
    ParameterKey=EnvironmentType,ParameterValue=production \
    ParameterKey=KeyPairName,ParameterValue=your-key-pair \
    ParameterKey=DBPassword,ParameterValue=YourSecurePassword123! \
    ParameterKey=ContentBucketName,ParameterValue=ai-sakhi-content \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 4: Monitor Deployment

Monitor stack creation progress:

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-main \
  --query 'Stacks[0].StackStatus'

# Watch stack events
aws cloudformation describe-stack-events \
  --stack-name ai-sakhi-main \
  --max-items 10
```

Deployment typically takes 20-30 minutes.

### Step 5: Deploy Application Code

Once infrastructure is ready, deploy your application:

```bash
# Package application
cd /path/to/ai-sakhi
zip -r ai-sakhi-app.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"

# Upload to S3
aws s3 cp ai-sakhi-app.zip s3://ai-sakhi-content-<account-id>/app/

# Extract on S3
aws s3 cp ai-sakhi-app.zip s3://ai-sakhi-content-<account-id>/app/
aws s3 sync . s3://ai-sakhi-content-<account-id>/app/ --exclude "*.git*"
```

### Step 6: Initialize Database

Connect to RDS and initialize the database schema:

```bash
# Get DB endpoint from CloudFormation outputs
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-sakhi-main \
  --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' \
  --output text)

# Connect to database (from EC2 instance or bastion host)
psql -h $DB_ENDPOINT -U aisakhi_admin -d aisakhi

# Run schema initialization
\i database/schema.sql
```

### Step 7: Verify Deployment

1. **Get Application URL:**
```bash
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-main \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text
```

2. **Test Health Endpoint:**
```bash
curl http://<alb-dns-name>/health
```

3. **Check CloudWatch Dashboard:**
```bash
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-main \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudWatchDashboardURL`].OutputValue' \
  --output text
```

## Configuration Parameters

### Network Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| VpcCIDR | 10.0.0.0/16 | VPC CIDR block |
| PublicSubnet1CIDR | 10.0.1.0/24 | Public subnet 1 CIDR |
| PublicSubnet2CIDR | 10.0.2.0/24 | Public subnet 2 CIDR |
| PrivateSubnet1CIDR | 10.0.11.0/24 | Private subnet 1 CIDR |
| PrivateSubnet2CIDR | 10.0.12.0/24 | Private subnet 2 CIDR |

### Application Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| InstanceType | t3.medium | EC2 instance type |
| MinSize | 2 | Minimum instances |
| MaxSize | 6 | Maximum instances |
| DesiredCapacity | 2 | Desired instances |
| ApplicationPort | 8080 | Application port |

### Database Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| DBInstanceClass | db.t3.medium | RDS instance type |
| DBAllocatedStorage | 20 | Storage size (GB) |
| DBUsername | aisakhi_admin | Master username |
| DBPassword | (required) | Master password |

## Post-Deployment Tasks

### 1. Configure DNS

Point your domain to the CloudFront distribution or ALB:

```bash
# Get CloudFront domain
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-main \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
  --output text
```

Create a CNAME record in your DNS provider:
- Name: `app.yourdomain.com`
- Type: CNAME
- Value: `<cloudfront-domain>`

### 2. Configure SSL/TLS

Request an ACM certificate:

```bash
aws acm request-certificate \
  --domain-name app.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

Update ALB listener to use HTTPS.

### 3. Set Up Monitoring Alerts

Configure SNS topic subscription for alarms:

```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:<account-id>:ai-sakhi-prod-alarms \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### 4. Configure Backup Strategy

Enable automated backups:

```bash
# RDS backups (already configured in template)
# DynamoDB point-in-time recovery (already enabled)

# S3 versioning (already enabled)
# Consider cross-region replication for disaster recovery
```

### 5. Load Initial Content

Upload initial content to S3:

```bash
# Upload audio files
aws s3 sync ./content/audio/ s3://ai-sakhi-content-<account-id>/audio/

# Upload video files
aws s3 sync ./content/video/ s3://ai-sakhi-content-<account-id>/video/

# Upload static assets
aws s3 sync ./static/ s3://ai-sakhi-static-assets-<account-id>/
```

## Updating the Stack

To update the infrastructure:

```bash
aws cloudformation update-stack \
  --stack-name ai-sakhi-main \
  --template-body file://cloudformation/main-stack.yaml \
  --parameters \
    ParameterKey=EnvironmentName,UsePreviousValue=true \
    ParameterKey=DesiredCapacity,ParameterValue=4 \
  --capabilities CAPABILITY_NAMED_IAM
```

## Scaling

### Horizontal Scaling (Add more instances)

Update Auto Scaling Group parameters:

```bash
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name ai-sakhi-prod-asg \
  --min-size 3 \
  --max-size 10 \
  --desired-capacity 4
```

### Vertical Scaling (Larger instances)

Update stack with new instance type:

```bash
aws cloudformation update-stack \
  --stack-name ai-sakhi-main \
  --use-previous-template \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=t3.large \
  --capabilities CAPABILITY_NAMED_IAM
```

## Troubleshooting

### Stack Creation Failed

1. Check CloudFormation events:
```bash
aws cloudformation describe-stack-events \
  --stack-name ai-sakhi-main \
  --max-items 20
```

2. Common issues:
   - **Insufficient permissions**: Ensure IAM user has required permissions
   - **Resource limits**: Check service quotas in AWS Console
   - **Invalid parameters**: Verify all parameter values

### Application Not Accessible

1. Check target group health:
```bash
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn>
```

2. Check EC2 instance logs:
```bash
aws logs tail /aws/ec2/ai-sakhi-prod/application --follow
```

3. Verify security groups allow traffic

### Database Connection Issues

1. Check security group rules
2. Verify database endpoint and credentials
3. Test connection from EC2 instance:
```bash
psql -h <db-endpoint> -U aisakhi_admin -d aisakhi
```

## Cost Optimization

### Development Environment

For development, use smaller instance types:

```yaml
InstanceType: t3.small
DBInstanceClass: db.t3.micro
MinSize: 1
MaxSize: 2
DesiredCapacity: 1
```

### Production Environment

For production, consider:

- Reserved Instances for baseline capacity
- Savings Plans for compute
- S3 Intelligent-Tiering
- RDS Reserved Instances

## Cleanup

To delete all resources:

```bash
# Delete main stack (will delete all nested stacks)
aws cloudformation delete-stack --stack-name ai-sakhi-main

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name ai-sakhi-main

# Manually delete S3 buckets (if not empty)
aws s3 rb s3://ai-sakhi-content-<account-id> --force
aws s3 rb s3://ai-sakhi-static-assets-<account-id> --force
aws s3 rb s3://ai-sakhi-cloudtrail-<account-id> --force
```

## Security Best Practices

1. **Use AWS Secrets Manager** for database credentials
2. **Enable MFA** for AWS account
3. **Implement least privilege** IAM policies
4. **Enable CloudTrail** for audit logging
5. **Use VPC endpoints** to avoid internet traffic
6. **Encrypt data** at rest and in transit
7. **Regular security audits** using AWS Security Hub
8. **Implement WAF** rules for ALB

## Support

For issues or questions:
- Check CloudWatch Logs
- Review CloudFormation events
- Consult AWS documentation
- Contact AWS Support

## Additional Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AI Sakhi Architecture Documentation](../AI-SAKHI-ARCHITECTURE-SUMMARY.md)
- [Application Test Report](../APPLICATION_TEST_REPORT.md)

---

**Version:** 1.0.0  
**Last Updated:** February 28, 2026  
**Maintained By:** AI Sakhi Development Team
