# AI Sakhi - Architecture Summary

## Project Overview

**AI Sakhi** is a voice-first health companion application designed to serve rural women and girls in India with accessible health education, safety awareness, and guidance. The application leverages AWS cloud services to provide multi-language support, voice interactions, and comprehensive health modules.

## Architecture Highlights

### Core Design Principles

1. **Voice-First Interface**: Primary interaction through speech for low-literacy users
2. **Multi-Language Support**: 6 languages (Hindi, English, Bengali, Tamil, Telugu, Marathi)
3. **Accessibility**: Audio-first content delivery with visual fallbacks
4. **Cultural Sensitivity**: Women-centric design with appropriate imagery and language
5. **Medical Boundaries**: Educational guidance without medical diagnosis
6. **Emergency Response**: Immediate connection to helplines and human support

### Technology Stack

#### Backend
- **Framework**: Flask (Python 3.10+)
- **Server**: EC2 instances with Auto Scaling
- **Port**: 8080
- **Session Management**: DynamoDB for state persistence
- **Content Storage**: AWS S3 for audio/video materials

#### Frontend
- **Web Technologies**: HTML5, CSS3, JavaScript
- **Voice Interface**: Web Speech API, WebRTC
- **Responsive Design**: Mobile-first approach
- **Branding**: AI Sakhi logo with mother-daughter imagery

#### AWS Services Integration

**AI/ML Services**:
- **AWS Transcribe**: Speech-to-text conversion (6 languages)
- **AWS Polly**: Text-to-speech synthesis with regional voices
- **AWS Translate**: Multi-language translation
- **Amazon Bedrock**: AI content processing and understanding

**Storage Services**:
- **S3**: Educational content (audio/video) and static assets
- **DynamoDB**: User sessions and interaction history
- **RDS**: Government schemes database

**Monitoring & Operations**:
- **CloudWatch**: Application metrics, performance monitoring, alerting
- **CloudTrail**: API logging, audit trail, security monitoring

**Integration Services**:
- **API Gateway**: Request routing and authentication
- **SNS**: SMS notifications for reminders and alerts
- **SQS**: Message queuing for async processing

**Networking**:
- **ELB**: Application Load Balancer for traffic distribution
- **Route 53**: DNS management
- **CloudFront**: CDN for content delivery

## Application Components

### 1. Core Services

#### Session Manager
- User state tracking
- Language preference management
- Interaction history
- Progress tracking across modules
- Session timeout handling (30 minutes)

#### Content Manager
- Educational content retrieval from S3
- Multi-language content delivery
- Content caching and optimization
- Safety validation before delivery

#### Speech Processor
- Speech-to-text conversion using AWS Transcribe
- Text-to-speech synthesis using AWS Polly
- Language detection
- Voice processing statistics

#### Voice Interface
- End-to-end voice interaction handling
- Audio input processing
- Response generation
- Fallback to text interface

### 2. Health Education Modules

#### Puberty Education Module
- Body changes during puberty
- Menstruation basics
- Hygiene practices
- Emotional changes
- Age-appropriate content

#### Safety & Mental Support Module
- Good touch vs. bad touch awareness
- Personal safety guidelines
- Emotional support resources
- Distress detection
- Emergency helpline connections

#### Menstrual Guide Module
- Product comparison (pads, cups, cloth)
- Cost analysis
- Hygiene best practices
- Product selection guidance
- Budget-based recommendations

#### Pregnancy Guidance Module
- Nutrition tips for pregnant women
- Danger signs recognition
- Prenatal appointment reminders
- Trimester-specific guidance
- Medical referral triggers

#### Government Resources Module
- Government health schemes information
  - Janani Suraksha Yojana (JSY)
  - Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)
  - Janani Shishu Suraksha Karyakram (JSSK)
  - Reproductive and Child Health (RCH)
  - Swasth Nari Scheme
- Eligibility criteria
- Application process
- Required documents
- Regional variations

### 3. Supporting Systems

#### Reminder System
- Prenatal appointment reminders
- Medication reminders
- Health checkup notifications
- Custom reminder creation
- SMS/push notification delivery

#### Content Safety Validator
- Medical boundary compliance
- Inappropriate content detection
- Response sanitization
- Medical referral triggers
- Safety warnings

#### Error Handler
- Graceful degradation
- Offline emergency access
- Fallback mechanisms
- User-friendly error messages
- Recovery options

## Data Models

### User Session
```python
{
    "session_id": "unique_identifier",
    "language_preference": "hi",
    "current_module": "puberty",
    "interaction_history": [],
    "emergency_contacts": {},
    "accessibility_preferences": {},
    "created_at": "2026-02-06T10:00:00Z",
    "last_active": "2026-02-06T10:30:00Z"
}
```

### Content Item
```python
{
    "content_id": "unique_identifier",
    "module_name": "puberty",
    "topic": "menstruation_basics",
    "content_type": "audio",
    "language_code": "hi",
    "s3_url": "s3://bucket/path/to/content.mp3",
    "duration_seconds": 180,
    "transcript": "Content transcript...",
    "safety_validated": true,
    "created_at": "2026-01-15T00:00:00Z"
}
```

### Voice Interaction
```python
{
    "interaction_id": "unique_identifier",
    "session_id": "session_id",
    "user_audio_transcript": "मुझे यौवनावस्था के बारे में जानकारी चाहिए",
    "system_response_text": "यौवनावस्था में शरीर में कई बदलाव होते हैं...",
    "system_audio_url": "s3://bucket/response.mp3",
    "language_code": "hi",
    "confidence_score": 0.95,
    "processing_time_ms": 1250,
    "timestamp": "2026-02-06T10:15:00Z"
}
```

### Government Scheme
```python
{
    "scheme_id": "JSY_001",
    "scheme_name": "Janani Suraksha Yojana",
    "scheme_type": "maternity",
    "eligibility_criteria": ["Pregnant women", "BPL families"],
    "benefits": ["Cash assistance", "Free delivery"],
    "application_process": "Visit nearest health center...",
    "required_documents": ["Aadhaar", "BPL card"],
    "contact_details": {"phone": "1800-xxx-xxxx"},
    "regional_variations": {},
    "language_code": "hi",
    "last_updated": "2026-01-01T00:00:00Z"
}
```

## Data Flow Diagrams

### Voice Interaction Flow
```
User Speaks
    ↓
Voice Interface (Web Speech API)
    ↓
AWS Transcribe (Speech-to-Text)
    ↓
Language Processor
    ↓
Content Manager → Amazon Bedrock (AI Processing)
    ↓
Response Generation
    ↓
AWS Polly (Text-to-Speech)
    ↓
Voice Interface
    ↓
User Hears Response
```

### Content Delivery Flow
```
User Request
    ↓
Session Manager (DynamoDB)
    ↓
Health Module Selection
    ↓
Content Manager
    ↓
S3 Content Retrieval
    ↓
Content Safety Validation
    ↓
Language-Specific Content
    ↓
User Interface
    ↓
User Receives Content
```

### Emergency Response Flow
```
Emergency Detected
    ↓
Emergency Connector
    ↓
├─→ Emergency Helplines (Direct Call)
├─→ SMS Alerts (SNS)
└─→ Medical Referral Guidance
    ↓
Immediate User Support
```

## Security Architecture

### Network Security
- **VPC**: Private network isolation
- **Security Groups**: Firewall rules for EC2 instances
- **Network ACLs**: Subnet-level protection
- **Private Subnets**: Database and backend services

### Application Security
- **IAM Roles**: Service-specific permissions
- **KMS**: Data encryption at rest
- **SSL/TLS**: Data encryption in transit
- **API Gateway**: Request authentication and rate limiting

### Data Security
- **S3 Encryption**: Server-side encryption for content
- **DynamoDB Encryption**: At-rest encryption
- **RDS Encryption**: Database encryption
- **Automated Backups**: Regular data backups
- **CloudTrail**: Audit logging for all API calls

## Scalability & Performance

### Auto Scaling
- **EC2 Auto Scaling**: Scale based on CPU/memory usage
- **Target Tracking**: Maintain optimal performance
- **Scheduled Scaling**: Handle predictable traffic patterns

### Load Balancing
- **Application Load Balancer**: Distribute traffic across instances
- **Health Checks**: Automatic unhealthy instance removal
- **Cross-Zone Load Balancing**: Even distribution

### Caching
- **CloudFront CDN**: Edge caching for static content
- **ElastiCache Redis**: Application-level caching
- **S3 Transfer Acceleration**: Faster content uploads

### Database Optimization
- **DynamoDB Auto Scaling**: Automatic capacity adjustment
- **RDS Read Replicas**: Distribute read traffic
- **Connection Pooling**: Efficient database connections

## Monitoring & Observability

### Application Metrics
- Request count and latency
- Error rates and types
- Voice processing success rates
- Module usage statistics
- Language distribution

### Infrastructure Metrics
- EC2 CPU and memory utilization
- Load balancer metrics
- Database performance
- S3 request metrics
- Lambda execution metrics

### Alerting
- High error rate alerts
- Performance degradation alerts
- Security incident alerts
- Cost anomaly alerts

### Logging
- Application logs (CloudWatch Logs)
- API access logs (CloudTrail)
- Load balancer access logs
- VPC flow logs

## Deployment Architecture

### Development Environment
- Local Flask development server
- Mock AWS services for testing
- Virtual environment isolation
- Git version control

### Production Environment
- **Availability Zones**: Multi-AZ deployment for high availability
- **EC2 Instances**: Auto-scaled across multiple AZs
- **RDS**: Primary in AZ-A, standby in AZ-B
- **S3**: Global service with cross-region replication
- **CloudFront**: Global CDN distribution

### CI/CD Pipeline
- Git repository (GitHub/GitLab)
- Automated testing
- Staging environment
- Blue-green deployment
- Rollback capabilities

## Cost Optimization

### Compute
- Right-sized EC2 instances
- Reserved instances for baseline capacity
- Spot instances for batch processing
- Lambda for event-driven tasks

### Storage
- S3 Intelligent-Tiering for content
- Lifecycle policies for old data
- Compression for audio/video files

### Data Transfer
- CloudFront for reduced data transfer costs
- VPC endpoints for AWS service access
- Compression for API responses

## Future Enhancements

### Planned Features
1. **Offline Mode**: Download content for offline access
2. **Video Consultations**: Connect with healthcare providers
3. **Community Forums**: Peer support and discussions
4. **Gamification**: Engagement through achievements
5. **Wearable Integration**: Health tracking devices
6. **Telemedicine**: Remote doctor consultations
7. **AI Chatbot**: 24/7 automated support
8. **Regional Dialects**: Support for more language variants

### Technical Improvements
1. **GraphQL API**: More efficient data fetching
2. **WebSocket**: Real-time communication
3. **Progressive Web App**: Better mobile experience
4. **Edge Computing**: Faster response times
5. **Machine Learning**: Personalized recommendations
6. **Blockchain**: Secure health records

## Documentation

### Available Documentation
1. **README.md**: Project overview and setup instructions
2. **CONTRIBUTING.md**: Contribution guidelines
3. **CHANGELOG.md**: Version history and changes
4. **GIT_WORKFLOW.md**: Git branching and commit conventions
5. **ai-sakhi-architecture-diagram.md**: Comprehensive Mermaid diagrams
6. **aws-diagram-mcp-setup-report.md**: MCP server setup and diagram generation
7. **Design Document**: `.kiro/specs/sakhi-saathi-ai/design.md`
8. **Requirements Document**: `.kiro/specs/sakhi-saathi-ai/requirements.md`
9. **Tasks Document**: `.kiro/specs/sakhi-saathi-ai/tasks.md`

### API Documentation
- Health check endpoint: `/health`
- Voice processing: `/api/voice/process`
- Text processing: `/api/text/process`
- Reminders: `/api/reminders`
- Emergency contacts: `/api/emergency`
- Language switching: `/language/<code>`
- Statistics: `/api/stats`

## Contact & Support

### Emergency Helplines
- **Women Helpline**: 1091
- **National Commission for Women**: 7827-170-170
- **Medical Emergency**: 108
- **Police**: 100

### Project Information
- **Version**: 1.0.0
- **License**: MIT (or appropriate license)
- **Repository**: [GitHub URL]
- **Documentation**: [Documentation URL]

## Conclusion

AI Sakhi represents a comprehensive, scalable, and culturally sensitive solution for providing health education to rural women and girls in India. The architecture leverages modern cloud technologies while maintaining accessibility and ease of use for the target audience. The voice-first approach, combined with multi-language support and emergency response capabilities, makes it a valuable tool for improving health literacy and outcomes in underserved communities.
