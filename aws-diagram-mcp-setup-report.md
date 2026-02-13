# AWS Diagram MCP Server Setup Report

## Status: Partial Success ⚠️

### What Worked ✅
1. **MCP Server Access**: Successfully connected to AWS Diagram MCP Server tools
2. **Icon Discovery**: Retrieved complete list of AWS service icons available
3. **Example Retrieval**: Got diagram code examples showing correct syntax
4. **Diagram Code Generation**: Created valid Python diagrams code for AI Sakhi architecture

### What Failed ❌
1. **Diagram Generation**: Windows compatibility issue with signal handling
   - Error: `AttributeError: module 'signal' has no attribute 'SIGALRM'`
   - Root Cause: SIGALRM is Unix-specific and not available on Windows
   - Impact: Cannot generate PNG diagrams directly on Windows

### Workaround Solutions 🔧

#### Option 1: Use WSL (Recommended)
Run the diagram generation inside WSL where Unix signals are supported:

```bash
# In WSL terminal
cd /mnt/c/path/to/your/project
python3 -c "
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.network import ELB, APIGateway
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.ml import Transcribe, Polly, Translate, Bedrock
from diagrams.aws.management import Cloudwatch, Cloudtrail
from diagrams.aws.integration import SNS
from diagrams.onprem.client import User

with Diagram('AI Sakhi Architecture', show=False, direction='TB', filename='generated-diagrams/ai-sakhi-architecture'):
    # [Full diagram code here]
    pass
"
```

#### Option 2: Use Online Mermaid Diagrams
The existing `ai-sakhi-architecture-diagram.md` file contains comprehensive Mermaid diagrams that render on GitHub/GitLab automatically.

#### Option 3: Manual Python Script
Create a standalone Python script and run it in a Linux environment or Docker container.

## AI Sakhi Architecture Diagram Code

### Complete Python Diagrams Code

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.network import ELB, APIGateway
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.ml import Transcribe, Polly, Translate, Bedrock
from diagrams.aws.management import Cloudwatch, Cloudtrail
from diagrams.aws.integration import SNS
from diagrams.onprem.client import User

with Diagram("AI Sakhi - Voice-First Health Companion Architecture", show=False, direction="TB"):
    # User Layer
    user = User("Rural Women & Girls")
    
    # Frontend Layer
    with Cluster("Frontend Layer"):
        web_app = EC2("Flask Web App\nPort 8080")
        voice_ui = Lambda("Voice Interface")
        lang_selector = Lambda("Language Selector")
    
    # API Gateway & Load Balancing
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
    
    # AWS AI/ML Services
    with Cluster("AWS AI/ML Services"):
        transcribe = Transcribe("Speech-to-Text")
        polly = Polly("Text-to-Speech")
        translate = Translate("Multi-language")
        bedrock = Bedrock("AI Processing")
    
    # Data Storage Layer
    with Cluster("Data Storage"):
        s3_content = S3("Health Content\nAudio/Video Files")
        s3_static = S3("Static Assets\nImages/CSS/JS")
        dynamodb = Dynamodb("User Sessions")
        rds = RDS("Government Schemes\nDatabase")
    
    # Monitoring & Operations
    with Cluster("Monitoring & Operations"):
        cloudwatch = Cloudwatch("Application Monitoring")
        cloudtrail = Cloudtrail("API Logging")
    
    # External Services
    with Cluster("External Integrations"):
        helpline = Lambda("Emergency Helplines")
        govt_api = Lambda("Government APIs")
        sms_service = SNS("SMS Notifications")
    
    # User to Frontend connections
    user >> Edge(label="Voice/Web Access") >> [web_app, voice_ui]
    user >> lang_selector
    
    # Frontend to Gateway
    [web_app, voice_ui, lang_selector] >> api_gateway
    api_gateway >> load_balancer
    load_balancer >> session_mgr
    
    # Session Manager to Modules
    session_mgr >> [puberty_mod, safety_mod, menstrual_mod, pregnancy_mod, govt_mod]
    session_mgr >> [emergency_svc, content_mgr, lang_processor]
    
    # Voice Processing Flow
    voice_ui >> Edge(label="Audio Input") >> transcribe
    lang_processor >> Edge(label="Generate Speech") >> polly
    lang_processor >> translate
    content_mgr >> Edge(label="AI Content") >> bedrock
    
    # Data Access
    content_mgr >> Edge(label="Fetch Content") >> s3_content
    web_app >> s3_static
    session_mgr >> Edge(label="Store Sessions") >> dynamodb
    govt_mod >> Edge(label="Query Schemes") >> rds
    
    # Emergency Services
    emergency_svc >> [helpline, sms_service]
    
    # Government Integration
    govt_mod >> govt_api
    
    # Monitoring
    [session_mgr, content_mgr, lang_processor] >> cloudwatch
    api_gateway >> cloudtrail
```

## Architecture Overview

### Key Components

#### 1. User Layer
- **Target Users**: Rural women and girls in India
- **Access Methods**: Voice-first interface, web browser

#### 2. Frontend Layer
- **Flask Web App**: Main application server running on EC2 (Port 8080)
- **Voice Interface**: Lambda function handling voice interactions
- **Language Selector**: Multi-language support (Hindi, English, Bengali, Tamil, Telugu, Marathi)

#### 3. API Gateway & Load Balancing
- **API Gateway**: Request routing and authentication
- **Application Load Balancer**: Distributes traffic across EC2 instances

#### 4. Core Application Services
- **Session Manager**: User state and progress tracking
- **Health Education Modules**:
  - Puberty Education: Body changes, menstruation, hygiene
  - Safety & Mental Support: Good/bad touch awareness, emotional support
  - Menstrual Guide: Product comparison and selection
  - Pregnancy Guidance: Nutrition tips, danger signs
  - Government Resources: Health schemes information
- **Emergency Connector**: Immediate connection to helplines
- **Content Manager**: Educational content retrieval
- **Language Processor**: Natural language understanding

#### 5. AWS AI/ML Services
- **AWS Transcribe**: Speech-to-text conversion (6 languages)
- **AWS Polly**: Text-to-speech synthesis with regional voices
- **AWS Translate**: Multi-language translation
- **Amazon Bedrock**: AI content processing and understanding

#### 6. Data Storage
- **S3 (Content)**: Audio/video educational materials
- **S3 (Static)**: Images, CSS, JavaScript files
- **DynamoDB**: User sessions and interaction history
- **RDS**: Government schemes database (JSY, PMSMA, JSSK, etc.)

#### 7. Monitoring & Operations
- **CloudWatch**: Application metrics, performance monitoring, alerting
- **CloudTrail**: API logging, audit trail, security monitoring

#### 8. External Integrations
- **Emergency Helplines**: Direct connection to medical/safety services
- **Government APIs**: Real-time scheme information
- **SNS**: SMS notifications for reminders and alerts

### Data Flow

1. **Voice Input Flow**:
   - User speaks → Voice Interface → AWS Transcribe → Text
   - Text → Language Processor → Content Manager → Response
   - Response → AWS Polly → Audio → User

2. **Content Delivery Flow**:
   - User request → Session Manager → Health Module
   - Health Module → Content Manager → S3 → Content
   - Content → User Interface → User

3. **Emergency Flow**:
   - Emergency detected → Emergency Connector
   - Emergency Connector → Helplines + SMS Alerts
   - Immediate response to user

### Technology Stack

- **Backend**: Python 3.10+, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Voice Processing**: AWS Transcribe, AWS Polly
- **AI/ML**: Amazon Bedrock
- **Storage**: AWS S3, DynamoDB, RDS
- **Monitoring**: CloudWatch, CloudTrail
- **Deployment**: EC2, ELB, API Gateway

### Security Features

- **VPC**: Private network isolation
- **Security Groups**: Firewall rules
- **IAM Roles**: Service permissions
- **KMS**: Data encryption at rest
- **SSL/TLS**: Data encryption in transit
- **CloudTrail**: Audit logging

### Scalability Features

- **Auto Scaling**: EC2 instances scale based on demand
- **Load Balancing**: Traffic distribution across instances
- **DynamoDB**: Auto-scaling NoSQL database
- **CloudFront CDN**: Content delivery optimization
- **ElastiCache**: Redis caching layer

## Next Steps

### To Generate PNG Diagram:

1. **Using WSL** (Recommended):
   ```bash
   # Install dependencies in WSL
   sudo apt-get update
   sudo apt-get install -y graphviz python3-pip
   pip3 install diagrams
   
   # Run the diagram generation
   python3 generate_diagram.py
   ```

2. **Using Docker**:
   ```bash
   docker run -v $(pwd):/diagrams python:3.10 bash -c "
   pip install diagrams && 
   cd /diagrams && 
   python generate_diagram.py
   "
   ```

3. **Using Online Tools**:
   - Visit [Mermaid Live Editor](https://mermaid.live/)
   - Copy Mermaid diagrams from `ai-sakhi-architecture-diagram.md`
   - Export as PNG/SVG

## Conclusion

While the MCP server has Windows compatibility limitations, we have:
1. ✅ Successfully accessed and tested the MCP server
2. ✅ Generated valid Python diagrams code
3. ✅ Documented comprehensive architecture
4. ✅ Provided multiple workaround solutions
5. ✅ Created detailed architecture documentation

The architecture diagram code is ready to use in Linux/WSL environments, and comprehensive Mermaid diagrams are available in the existing documentation.
