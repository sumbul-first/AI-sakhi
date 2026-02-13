#!/usr/bin/env python3
"""
AI Sakhi Architecture Diagram Generator

This script generates a comprehensive AWS architecture diagram for the AI Sakhi
Voice-First Health Companion application using the Python diagrams library.

Requirements:
    - Python 3.7+
    - diagrams library: pip install diagrams
    - graphviz: sudo apt-get install graphviz (Linux) or brew install graphviz (Mac)

Usage:
    python3 generate_ai_sakhi_diagram.py

Output:
    - PNG file: generated-diagrams/ai_sakhi_voice_first_health_companion_architecture.png
"""

import os
import sys

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2, Lambda
    from diagrams.aws.network import ELB, APIGateway
    from diagrams.aws.database import RDS, Dynamodb
    from diagrams.aws.storage import S3
    from diagrams.aws.ml import Transcribe, Polly, Translate, Bedrock
    from diagrams.aws.management import Cloudwatch, Cloudtrail
    from diagrams.aws.integration import SNS
    from diagrams.onprem.client import User
except ImportError as e:
    print(f"Error: Missing required library - {e}")
    print("\nPlease install required dependencies:")
    print("  pip install diagrams")
    print("  sudo apt-get install graphviz  # On Linux")
    print("  brew install graphviz          # On macOS")
    sys.exit(1)


def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = "generated-diagrams"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    return output_dir


def generate_architecture_diagram():
    """Generate the AI Sakhi architecture diagram."""
    print("Generating AI Sakhi Architecture Diagram...")
    
    output_dir = create_output_directory()
    output_path = os.path.join(output_dir, "ai_sakhi_architecture")
    
    with Diagram(
        "AI Sakhi - Voice-First Health Companion Architecture",
        show=False,
        direction="TB",
        filename=output_path,
        outformat="png"
    ):
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
    
    print(f"✅ Diagram generated successfully: {output_path}.png")
    return f"{output_path}.png"


def generate_simplified_diagram():
    """Generate a simplified version of the architecture diagram."""
    print("\nGenerating Simplified Architecture Diagram...")
    
    output_dir = create_output_directory()
    output_path = os.path.join(output_dir, "ai_sakhi_architecture_simplified")
    
    with Diagram(
        "AI Sakhi - Simplified Architecture",
        show=False,
        direction="LR",
        filename=output_path,
        outformat="png"
    ):
        # User
        user = User("Rural Women\n& Girls")
        
        # Frontend
        with Cluster("Frontend"):
            web = EC2("Flask App")
            voice = Lambda("Voice UI")
        
        # Backend Services
        with Cluster("Backend Services"):
            session = Lambda("Session\nManager")
            modules = Lambda("Health\nModules")
        
        # AWS Services
        with Cluster("AWS Services"):
            ai_services = [
                Transcribe("Transcribe"),
                Polly("Polly"),
                Bedrock("Bedrock")
            ]
        
        # Storage
        with Cluster("Storage"):
            storage = [
                S3("S3 Content"),
                Dynamodb("DynamoDB"),
                RDS("RDS")
            ]
        
        # Monitoring
        monitoring = Cloudwatch("CloudWatch")
        
        # Connections
        user >> [web, voice]
        [web, voice] >> session
        session >> modules
        voice >> ai_services
        modules >> storage
        [session, modules] >> monitoring
    
    print(f"✅ Simplified diagram generated: {output_path}.png")
    return f"{output_path}.png"


def main():
    """Main function to generate all diagrams."""
    print("=" * 70)
    print("AI Sakhi Architecture Diagram Generator")
    print("=" * 70)
    print()
    
    try:
        # Generate full architecture diagram
        full_diagram = generate_architecture_diagram()
        
        # Generate simplified diagram
        simplified_diagram = generate_simplified_diagram()
        
        print()
        print("=" * 70)
        print("✅ All diagrams generated successfully!")
        print("=" * 70)
        print(f"\nGenerated files:")
        print(f"  1. {full_diagram}")
        print(f"  2. {simplified_diagram}")
        print()
        print("You can now view these PNG files in your file explorer or image viewer.")
        
    except Exception as e:
        print(f"\n❌ Error generating diagrams: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure graphviz is installed:")
        print("     - Linux: sudo apt-get install graphviz")
        print("     - macOS: brew install graphviz")
        print("  2. Ensure diagrams library is installed:")
        print("     - pip install diagrams")
        print("  3. Check that you have write permissions in the current directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
