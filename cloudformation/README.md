# AI Sakhi - CloudFormation Templates

## Overview

This directory contains AWS CloudFormation templates for deploying the complete AI Sakhi infrastructure on AWS.

## Template Structure

```
cloudformation/
├── main-stack.yaml                      # Master template - Multi-AZ (High Availability)
├── main-stack-single-az.yaml            # Master template - Single-AZ (Cost Optimized)
├── network-stack.yaml                   # VPC, subnets, NAT gateways (Multi-AZ)
├── network-stack-single-az.yaml         # VPC, subnets, NAT gateway (Single-AZ)
├── security-stack.yaml                  # Security groups, IAM roles, KMS keys
├── storage-stack.yaml                   # S3 buckets, DynamoDB tables, SNS topics
├── database-stack.yaml                  # RDS PostgreSQL Multi-AZ with read replica
├── database-stack-single-az.yaml        # RDS PostgreSQL Single-AZ (no replica)
├── application-stack.yaml               # EC2, ALB, Auto Scaling (Multi-AZ)
├── application-stack-single-az.yaml     # EC2, ALB, Auto Scaling (Single-AZ)
├── monitoring-stack.yaml                # CloudWatch, CloudTrail, alarms
├── parameters-dev.json                  # Development environment parameters
├── parameters-prod.json                 # Production environment parameters
├── parameters-cost-optimized.json       # Cost-optimized Single-AZ parameters
├── DEPLOYMENT_GUIDE.md                  # Comprehensive deployment guide
├── COST_OPTIMIZATION_GUIDE.md           # Cost comparison and optimization tips
├── QUICK_START_SINGLE_AZ.md             # Quick start for Single-AZ deployment
└── README.md                            # This file
```

## Deployment Options

### Option 1: Multi-AZ (High Availability) 🏢
- **Cost**: ~$500-800/month
- **Availability**: 99.95%+
- **Use Case**: Production with high availability requirements
- **Templates**: `main-stack.yaml` + multi-AZ templates

### Option 2: Single-AZ (Cost Optimized) 💰
- **Cost**: ~$145-250/month (40-70% savings)
- **Availability**: ~99.5%
- **Use Case**: Development, testing, cost-sensitive deployments
- **Templates**: `main-stack-single-az.yaml` + single-AZ templates

## Quick Start

### Deploy Cost-Optimized (Single-AZ) - Recommended for Dev/Test

```bash
aws cloudformation create-stack \
  --stack-name ai-sakhi-cost-opt \
  --template-body file://main-stack-single-az.yaml \
  --parameters file://parameters-cost-optimized.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

**Cost**: ~$145-250/month | **Deployment Time**: ~20-25 minutes

See [QUICK_START_SINGLE_AZ.md](QUICK_START_SINGLE_AZ.md) for detailed instructions.

### Deploy High Availability (Multi-AZ) - Recommended for Production

```bash
aws cloudformation create-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://main-stack.yaml \
  --parameters file://parameters-prod.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

**Cost**: ~$500-800/month | **Deployment Time**: ~25-30 minutes

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## Stack Dependencies

```
main-stack
├── network-stack (no dependencies)
├── security-stack (depends on: network-stack)
├── storage-stack (no dependencies)
├── database-stack (depends on: network-stack, security-stack)
├── application-stack (depends on: all above)
└── monitoring-stack (depends on: application-stack)
```

## Resources Created

### Network Resources
- 1 VPC
- 2 Public Subnets (Multi-AZ)
- 2 Private Subnets (Multi-AZ)
- 1 Internet Gateway
- 2 NAT Gateways
- Route Tables
- VPC Endpoints (S3, DynamoDB)

### Security Resources
- 3 Security Groups (ALB, EC2, RDS)
- IAM Roles and Policies
- KMS Encryption Keys
- Instance Profiles

### Storage Resources
- 2 S3 Buckets (content, static assets)
- 3 DynamoDB Tables (sessions, interactions, reminders)
- 1 SNS Topic (notifications)

### Database Resources
- 1 RDS PostgreSQL Instance (Multi-AZ)
- 1 Read Replica
- DB Subnet Group
- DB Parameter Group

### Application Resources
- Application Load Balancer
- Auto Scaling Group (2-6 instances)
- Launch Template
- Target Group
- CloudFront Distribution

### Monitoring Resources
- CloudWatch Dashboard
- CloudWatch Log Groups
- CloudWatch Alarms
- CloudTrail
- SNS Alarm Topic

## Estimated Costs

### Single-AZ Deployment (Cost Optimized)
- **Monthly Cost**: ~$145-250
  - EC2 (1-2x t3.micro/small): ~$7-30
  - RDS (1x db.t3.micro, Single-AZ): ~$15
  - NAT Gateway (1x): ~$32
  - ALB: ~$25
  - S3, DynamoDB, CloudFront: ~$23
  - Data Transfer: ~$5
  - CloudWatch: ~$10
  - Other services: ~$5

**Savings vs Multi-AZ**: 40-70% (~$300-450/month)

### Multi-AZ Deployment (High Availability)
- **Monthly Cost**: ~$500-800
  - EC2 (2-4x t3.medium): ~$120-240
  - RDS (1x db.t3.medium Multi-AZ + replica): ~$120
  - NAT Gateway (2x): ~$64
  - ALB: ~$25
  - CloudFront: ~$20
  - S3, DynamoDB: ~$42
  - Data Transfer: ~$20
  - CloudWatch: ~$30
  - Other services: ~$10

*Costs vary based on usage, data transfer, and region*

See [COST_OPTIMIZATION_GUIDE.md](COST_OPTIMIZATION_GUIDE.md) for detailed cost comparison.

## Parameters

### Required Parameters
- `KeyPairName`: EC2 key pair for SSH access
- `DBPassword`: Database master password (min 8 characters)

### Optional Parameters (with defaults)
- `EnvironmentName`: Environment prefix (default: ai-sakhi)
- `EnvironmentType`: development/staging/production (default: development)
- `InstanceType`: EC2 instance type (default: t3.medium)
- `DBInstanceClass`: RDS instance type (default: db.t3.medium)
- `MinSize`: Minimum EC2 instances (default: 2)
- `MaxSize`: Maximum EC2 instances (default: 6)

See `parameters-dev.json` and `parameters-prod.json` for complete parameter lists.

## Outputs

After successful deployment, the stack provides:

- `ApplicationURL`: Load Balancer URL
- `CloudFrontURL`: CDN URL
- `ContentBucketName`: S3 content bucket
- `SessionTableName`: DynamoDB session table
- `DBEndpoint`: Database endpoint
- `CloudWatchDashboardURL`: Monitoring dashboard

## Validation

Validate templates before deployment:

```bash
# Validate main stack
aws cloudformation validate-template \
  --template-body file://main-stack.yaml

# Validate all templates
for template in *.yaml; do
  echo "Validating $template..."
  aws cloudformation validate-template --template-body file://$template
done
```

## Update Stack

To update an existing stack:

```bash
aws cloudformation update-stack \
  --stack-name ai-sakhi-prod \
  --template-body file://main-stack.yaml \
  --parameters file://parameters-prod.json \
  --capabilities CAPABILITY_NAMED_IAM
```

## Delete Stack

To delete all resources:

```bash
# Delete main stack (cascades to nested stacks)
aws cloudformation delete-stack --stack-name ai-sakhi-prod

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name ai-sakhi-prod
```

**Note**: S3 buckets with content must be emptied manually before deletion.

## Monitoring Deployment

### Check Stack Status

```bash
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-prod \
  --query 'Stacks[0].StackStatus'
```

### Watch Stack Events

```bash
aws cloudformation describe-stack-events \
  --stack-name ai-sakhi-prod \
  --max-items 10
```

### Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name ai-sakhi-prod \
  --query 'Stacks[0].Outputs'
```

## Troubleshooting

### Common Issues

1. **Stack creation fails with "Insufficient permissions"**
   - Ensure IAM user has CloudFormation, EC2, RDS, S3, DynamoDB permissions
   - Add `CAPABILITY_NAMED_IAM` capability

2. **Resource limit exceeded**
   - Check AWS service quotas
   - Request limit increase if needed

3. **Template validation errors**
   - Run `aws cloudformation validate-template`
   - Check YAML syntax

4. **Nested stack failures**
   - Check individual stack events
   - Verify template URLs are accessible

### Debug Commands

```bash
# Get detailed error information
aws cloudformation describe-stack-events \
  --stack-name ai-sakhi-prod \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'

# Check nested stack status
aws cloudformation list-stacks \
  --stack-status-filter CREATE_FAILED UPDATE_FAILED

# View stack resources
aws cloudformation describe-stack-resources \
  --stack-name ai-sakhi-prod
```

## Best Practices

1. **Use Parameter Files**: Store parameters in JSON files for repeatability
2. **Version Control**: Keep templates in Git
3. **Test in Dev First**: Always test changes in development before production
4. **Use Change Sets**: Preview changes before applying
5. **Tag Resources**: Use consistent tagging strategy
6. **Enable Termination Protection**: For production stacks
7. **Regular Backups**: Enable automated backups for databases
8. **Monitor Costs**: Use AWS Cost Explorer and set up billing alerts

## Security Considerations

1. **Secrets Management**: Use AWS Secrets Manager for sensitive data
2. **Encryption**: All data encrypted at rest and in transit
3. **Network Isolation**: Private subnets for application and database
4. **Least Privilege**: IAM roles follow least privilege principle
5. **Audit Logging**: CloudTrail enabled for all API calls
6. **Security Groups**: Restrictive ingress rules
7. **VPC Endpoints**: Avoid internet traffic for AWS services

## Additional Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Comprehensive deployment instructions
- [Architecture Summary](../AI-SAKHI-ARCHITECTURE-SUMMARY.md) - Application architecture
- [Application Test Report](../APPLICATION_TEST_REPORT.md) - Testing documentation

## Support

For issues or questions:
- Review CloudFormation events and logs
- Check CloudWatch Logs for application errors
- Consult AWS CloudFormation documentation
- Contact AWS Support for infrastructure issues

## Version History

- **v1.0.0** (2026-02-28): Initial release
  - Complete infrastructure templates
  - Multi-AZ deployment
  - Auto Scaling and Load Balancing
  - Monitoring and logging

---

**Maintained By**: AI Sakhi Development Team  
**License**: MIT  
**Repository**: https://github.com/sumbul-first/AI-sakhi.git
