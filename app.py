#!/usr/bin/env python3
import os
import aws_cdk as cdk
from infrastructure.stacks.construction.contact_stack_construction import ContactConstructionStack

app = cdk.App()

# Get account from environment
env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'eu-central-1')
)

# One stack for portfolio
stack = ContactConstructionStack(
    app,
    "RanjdarGroup-Portfolio-Stack",
    env=env
)

app.synth()