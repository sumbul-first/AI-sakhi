# AI Sakhi - Comprehensive Architecture Diagram

## Overview
This document provides a comprehensive architecture diagram for the AI Sakhi Voice-First Health Companion application, designed to serve rural women and girls with health education and guidance.

## 📋 Related Documentation

For additional architecture resources, see:
- **Architecture Summary**: `AI-SAKHI-ARCHITECTURE-SUMMARY.md` - Comprehensive overview of the entire system
- **Diagram Generation Guide**: `DIAGRAM-GENERATION-GUIDE.md` - Instructions for generating PNG diagrams
- **Python Script**: `generate_ai_sakhi_diagram.py` - Automated diagram generation script
- **MCP Setup Report**: `aws-diagram-mcp-setup-report.md` - MCP server setup and troubleshooting

## Main Architecture Diagram

### Mermaid Diagram (GitHub/GitLab Compatible)

```mermaid
graph TB
    %% User Layer
    U[👩‍🦰 Rural Women & Girls]
    
    %% Frontend Layer
    subgraph "Frontend Layer"
        WA[🌐 Flask Web App<br/>Port 8080]
        VI[🎤 Voice Interface]
        LS[🌍 Language Selector]
    end
    
    %% API Gateway Layer
    subgraph "API Gateway & Load Balancing"
        AG[🚪 API Gateway]
        LB[⚖️ Application Load Balancer]
    end
    
    %% Core Application Services
    subgraph "Core Application Services"
        SM[🎯 Session Manager]
        
        subgraph "Health Education Modules"
            PE[🌸 Puberty Education]
            SS[🛡️ Safety & Mental Support]
            MG[🩸 Menstrual Guide]
            PG[🤱 Pregnancy Guidance]
            GR[🏛️ Government Resources]
        end
        
        EC[🚨 Emergency Connector]
        CM[📚 Content Manager]
        LP[🗣️ Language Processor]
    end
    
    %% AI/ML Services Layer
    subgraph "AWS AI/ML Services"
        TR[🎙️ AWS Transcribe<br/>Speech-to-Text]
        PO[🔊 AWS Polly<br/>Text-to-Speech]
        TL[🌐 AWS Translate<br/>Multi-language]
        BR[🧠 Amazon Bedrock<br/>AI Processing]
    end
    
    %% Data Storage Layer
    subgraph "Data Storage"
        S3C[📦 S3 Health Content<br/>Audio/Video Files]
        S3S[🎨 S3 Static Assets<br/>Images/CSS/JS]
        DDB[🗄️ DynamoDB<br/>User Sessions]
        RDS[🏛️ RDS Database<br/>Government Schemes]
    end
    
    %% Monitoring & Operations
    subgraph "Monitoring & Operations"
        CW[📊 CloudWatch<br/>Application Monitoring]
        CT[📝 CloudTrail<br/>API Logging]
    end
    
    %% External Services
    subgraph "External Integrations"
        HL[📞 Emergency Helplines]
        GA[🏛️ Government APIs]
        SMS[📱 SNS SMS Service]
    end
    
    %% User Interactions
    U --> WA
    U --> VI
    
    %% Frontend to Gateway
    WA --> AG
    VI --> AG
    LS --> AG
    
    %% Gateway Flow
    AG --> LB
    LB --> SM
    
    %% Session Manager Coordination
    SM --> PE
    SM --> SS
    SM --> MG
    SM --> PG
    SM --> GR
    SM --> EC
    SM --> CM
    SM --> LP
    
    %% Voice Processing Flow
    VI --> TR
    LP --> PO
    LP --> TL
    CM --> BR
    
    %% Data Access
    CM --> S3C
    WA --> S3S
    SM --> DDB
    GR --> RDS
    
    %% Emergency Services
    EC --> HL
    EC --> SMS
    
    %% Government Integration
    GR --> GA
    
    %% Monitoring
    SM --> CW
    CM --> CW
    LP --> CW
    AG --> CT
```

## Voice Processing Flow Diagram

```mermaid
sequenceDiagram
    participant U as 👩‍🦰 User
    participant VI as 🎤 Voice Interface
    participant TR as 🎙️ AWS Transcribe
    participant LP as 🗣️ Language Processor
    participant CM as 📚 Content Manager
    participant BR as 🧠 Bedrock
    participant PO as 🔊 AWS Polly
    participant S3 as 📦 S3 Content
    
    U->>VI: Speaks in local language
    VI->>TR: Send audio data
    TR->>LP: Return transcribed text
    LP->>CM: Process query
    CM->>BR: Get AI response
    CM->>S3: Fetch relevant content
    S3->>CM: Return content
    CM->>LP: Prepare response
    LP->>PO: Convert to speech
    PO->>VI: Return audio response
    VI->>U: Play audio response
```

## Emergency Response Flow

```mermaid
flowchart TD
    A[🚨 Emergency Detected] --> B{Emergency Type?}
    
    B -->|Medical Emergency| C[🏥 Medical Helpline]
    B -->|Safety Threat| D[👮‍♀️ Police/Safety Helpline]
    B -->|Mental Health Crisis| E[🧠 Counseling Helpline]
    B -->|Pregnancy Danger Signs| F[🤱 Maternal Health Services]
    
    C --> G[📱 SMS Alert to Contacts]
    D --> G
    E --> G
    F --> G
    
    G --> H[📍 Location Services]
    H --> I[🚑 Emergency Response]
```

## Data Model Relationships

```mermaid
erDiagram
    UserSession {
        string session_id PK
        string language_preference
        string current_module
        json interaction_history
        json emergency_contacts
        json accessibility_preferences
        datetime created_at
        datetime last_active
    }
    
    ContentItem {
        string content_id PK
        string module_name
        string topic
        string content_type
        string language_code
        string s3_url
        int duration_seconds
        text transcript
        boolean safety_validated
        datetime created_at
    }
    
    VoiceInteraction {
        string interaction_id PK
        string session_id FK
        text user_audio_transcript
        text system_response_text
        string system_audio_url
        string language_code
        float confidence_score
        int processing_time_ms
        datetime timestamp
    }
    
    GovernmentScheme {
        string scheme_id PK
        string scheme_name
        string scheme_type
        json eligibility_criteria
        json benefits
        text application_process
        json required_documents
        json contact_details
        json regional_variations
        string language_code
        datetime last_updated
    }
    
    EmergencyContact {
        string contact_id PK
        string contact_type
        string phone_number
        string region
        json language_support
        string availability_hours
        text description
    }
    
    UserSession ||--o{ VoiceInteraction : "has"
    ContentItem ||--o{ VoiceInteraction : "references"
    UserSession ||--o{ EmergencyContact : "uses"
    GovernmentScheme ||--o{ ContentItem : "provides"
```

## AWS Services Integration Map

```mermaid
mindmap
  root((AI Sakhi<br/>AWS Services))
    (Compute)
      EC2
        Flask Web App
        Load Balancer
      Lambda
        Voice Processing
        Content Management
        Health Modules
    (Storage)
      S3
        Health Content
        Static Assets
        Audio Files
        Video Files
      DynamoDB
        User Sessions
        Interaction History
      RDS
        Government Schemes
        Emergency Contacts
    (AI/ML)
      Transcribe
        Speech Recognition
        Multi-language Support
      Polly
        Text-to-Speech
        Regional Voices
      Translate
        Language Translation
        Content Localization
      Bedrock
        AI Content Processing
        Natural Language Understanding
    (Integration)
      API Gateway
        Request Routing
        Authentication
        Rate Limiting
      SNS
        SMS Notifications
        Emergency Alerts
      SQS
        Message Queuing
        Async Processing
    (Monitoring)
      CloudWatch
        Application Metrics
        Performance Monitoring
        Alerting
      CloudTrail
        API Logging
        Audit Trail
        Security Monitoring
```

## Component Interaction Matrix

| Component | Transcribe | Polly | S3 | DynamoDB | RDS | Bedrock | SNS |
|-----------|------------|-------|----|---------|----|---------|-----|
| Voice Interface | ✅ Input | ✅ Output | ❌ | ❌ | ❌ | ❌ | ❌ |
| Session Manager | ❌ | ❌ | ❌ | ✅ Read/Write | ❌ | ❌ | ❌ |
| Content Manager | ❌ | ❌ | ✅ Read | ❌ | ❌ | ✅ Process | ❌ |
| Language Processor | ❌ | ✅ Generate | ❌ | ❌ | ❌ | ✅ Process | ❌ |
| Health Modules | ❌ | ❌ | ✅ Read | ❌ | ❌ | ✅ Process | ❌ |
| Government Module | ❌ | ❌ | ✅ Read | ❌ | ✅ Read | ✅ Process | ❌ |
| Emergency Connector | ❌ | ❌ | ❌ | ❌ | ✅ Read | ❌ | ✅ Send |

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development Environment"
        DEV[💻 Local Development<br/>Flask + Virtual Env]
    end
    
    subgraph "AWS Cloud Environment"
        subgraph "Availability Zone A"
            EC2A[🖥️ EC2 Instance A<br/>Flask App]
            RDSA[🗄️ RDS Primary<br/>Government Data]
        end
        
        subgraph "Availability Zone B"
            EC2B[🖥️ EC2 Instance B<br/>Flask App]
            RDSB[🗄️ RDS Standby<br/>Backup]
        end
        
        subgraph "Global Services"
            CF[🌐 CloudFront<br/>CDN]
            S3G[📦 S3 Global<br/>Content Storage]
            R53[🌍 Route 53<br/>DNS]
        end
    end
    
    DEV -->|Deploy| EC2A
    DEV -->|Deploy| EC2B
    
    R53 --> CF
    CF --> EC2A
    CF --> EC2B
    CF --> S3G
    
    EC2A --> RDSA
    EC2B --> RDSA
    RDSA -.->|Replication| RDSB
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            VPC[🔒 VPC<br/>Private Network]
            SG[🛡️ Security Groups<br/>Firewall Rules]
            NACL[🚧 Network ACLs<br/>Subnet Protection]
        end
        
        subgraph "Application Security"
            IAM[👤 IAM Roles<br/>Service Permissions]
            KMS[🔐 KMS<br/>Data Encryption]
            SSL[🔒 SSL/TLS<br/>Data in Transit]
        end
        
        subgraph "Data Security"
            ENC[🔐 S3 Encryption<br/>Data at Rest]
            BACKUP[💾 Automated Backups<br/>Data Recovery]
            AUDIT[📋 CloudTrail<br/>Audit Logging]
        end
    end
    
    VPC --> SG
    SG --> NACL
    IAM --> KMS
    KMS --> SSL
    SSL --> ENC
    ENC --> BACKUP
    BACKUP --> AUDIT
```

## Performance & Scalability

```mermaid
graph TD
    subgraph "Load Distribution"
        ALB[⚖️ Application Load Balancer]
        ASG[📈 Auto Scaling Group]
        EC2_1[🖥️ EC2 Instance 1]
        EC2_2[🖥️ EC2 Instance 2]
        EC2_N[🖥️ EC2 Instance N]
    end
    
    subgraph "Caching Layer"
        CF[🌐 CloudFront CDN]
        REDIS[⚡ ElastiCache Redis]
    end
    
    subgraph "Database Scaling"
        RDS_PRIMARY[🗄️ RDS Primary]
        RDS_REPLICA[🗄️ Read Replica]
        DDB[📊 DynamoDB<br/>Auto Scaling]
    end
    
    ALB --> ASG
    ASG --> EC2_1
    ASG --> EC2_2
    ASG --> EC2_N
    
    CF --> ALB
    EC2_1 --> REDIS
    EC2_2 --> REDIS
    EC2_N --> REDIS
    
    EC2_1 --> RDS_PRIMARY
    EC2_2 --> RDS_REPLICA
    EC2_N --> RDS_REPLICA
    
    EC2_1 --> DDB
    EC2_2 --> DDB
    EC2_N --> DDB
```

## How to Use These Diagrams

### 1. GitHub/GitLab Rendering
These Mermaid diagrams will render automatically in markdown files on GitHub and GitLab.

### 2. VS Code
Install the "Mermaid Preview" extension to view diagrams locally.

### 3. Online Tools
- Copy diagram code to [Mermaid Live Editor](https://mermaid.live/)
- Use [draw.io](https://app.diagrams.net/) for interactive versions
- Export to PNG, SVG, or PDF formats

### 4. Documentation Integration
- Include in technical documentation
- Use in architecture reviews
- Reference in development planning

## AWS Diagram MCP Server Code

For when the Windows compatibility issue is resolved, here's the Python code for the AWS Diagram MCP Server:

```python
# AI Sakhi Architecture Diagram - AWS MCP Server Code
with Diagram("AI Sakhi - Voice-First Health Companion", show=False, direction="TB"):
    # User Layer
    user = User("Rural Women & Girls")
    
    # Frontend Layer
    with Cluster("Frontend Layer"):
        web_app = EC2("Flask Web App (Port 8080)")
        voice_ui = Lambda("Voice Interface")
        lang_selector = Lambda("Language Selector")
    
    # API Gateway Layer
    with Cluster("API Gateway & Load Balancing"):
        api_gateway = APIGateway("API Gateway")
        load_balancer = ELB("Application Load Balancer")
    
    # Core Application Services
    with Cluster("Core Application Services"):
        session_mgr = Lambda("Session Manager")
        
        with Cluster("Health Education Modules"):
            puberty_mod = Lambda("Puberty Education")
            safety_mod = Lambda("Safety & Mental Support")
            menstrual_mod = Lambda("Menstrual Guide")
            pregnancy_mod = Lambda("Pregnancy Guidance")
            govt_mod = Lambda("Government Resources")
        
        emergency_svc = Lambda("Emergency Connector")
        content_mgr = Lambda("Content Manager")
        lang_processor = Lambda("Language Processor")
    
    # AI/ML Services Layer
    with Cluster("AWS AI/ML Services"):
        transcribe = Transcribe("Speech-to-Text")
        polly = Polly("Text-to-Speech")
        translate = Translate("Multi-language Support")
        bedrock = Bedrock("AI Content Processing")
    
    # Data Storage Layer
    with Cluster("Data Storage"):
        s3_content = S3("Health Content (Audio/Video)")
        s3_static = S3("Static Assets (Images/CSS/JS)")
        dynamodb = Dynamodb("User Sessions")
        rds = RDS("Government Schemes Database")
    
    # Monitoring & Operations
    with Cluster("Monitoring & Operations"):
        cloudwatch = CloudWatch("Application Monitoring")
        cloudtrail = CloudTrail("API Logging")
    
    # External Services
    with Cluster("External Integrations"):
        helpline_api = Lambda("Emergency Helplines")
        govt_api = Lambda("Government APIs")
        sms_service = SNS("SMS Notifications")
    
    # Connection flows
    user >> [web_app, voice_ui]
    [web_app, voice_ui, lang_selector] >> api_gateway
    api_gateway >> load_balancer >> session_mgr
    
    session_mgr >> [puberty_mod, safety_mod, menstrual_mod, pregnancy_mod, govt_mod]
    session_mgr >> [emergency_svc, content_mgr, lang_processor]
    
    voice_ui >> transcribe
    lang_processor >> [polly, translate]
    content_mgr >> bedrock
    
    content_mgr >> s3_content
    web_app >> s3_static
    session_mgr >> dynamodb
    govt_mod >> rds
    
    emergency_svc >> [helpline_api, sms_service]
    govt_mod >> govt_api
    
    [session_mgr, content_mgr, lang_processor] >> cloudwatch
    api_gateway >> cloudtrail
```

This comprehensive architecture diagram provides multiple views and formats for the AI Sakhi application, suitable for different audiences and use cases.