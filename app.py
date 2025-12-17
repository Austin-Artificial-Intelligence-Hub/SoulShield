#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import aws_cdk as cdk
from stacks.chatbot_stack import ChatbotStack

load_dotenv()

app = cdk.App()

ChatbotStack(
    app,
    "PrivacyChatbotStack",
    env=cdk.Environment(
        account=os.getenv("AWS_ACCOUNT_ID", os.getenv("CDK_DEFAULT_ACCOUNT")),
        region=os.getenv("AWS_REGION", "us-east-1"),
    ),
)

app.synth()
