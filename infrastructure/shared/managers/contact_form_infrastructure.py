"""
Shared contact form infrastructure manager.
Creates all AWS resources needed for contact form functionality as one unit.
Reusable across all business units (construction, cosmetics, retail, etc.).
"""

from aws_cdk import (
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct
from typing import Dict, Any


def create_contact_form_infrastructure(scope: Construct, business_unit: str) -> Dict[str, Any]:
    """
    Creates complete contact form infrastructure for any business unit.

    This single function creates:
    - DynamoDB table for storing submissions
    - Lambda function for processing forms
    - API Gateway REST API with /contact endpoint
    - All necessary IAM permissions

    Args:
        scope: The CDK construct scope (usually the stack)
        business_unit: The business unit (construction, cosmetics, retail, etc.)

    Returns:
        Dict containing created resources: {
            'table': DynamoDB table,
            'lambda': Lambda function,
            'api': API Gateway REST API
        }
    """

    # DATABASE (DynamoDB)
    #---------------------
    # NoSQL table to store contact form submissions
    table = dynamodb.Table(
        scope, f"{business_unit}-contact-table",
        table_name=f"RanjdarGroup-{business_unit.title()}ContactForm",

        # Primary key setup - need both pk and sk for DynamoDB
        partition_key=dynamodb.Attribute(
            name="pk",
            type=dynamodb.AttributeType.STRING
        ),
        sort_key=dynamodb.Attribute(
            name="sk",
            type=dynamodb.AttributeType.STRING
        ),

        # Pay per request = no monthly fee, only pay when used
        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,

        # DESTROY = delete table when stack deleted (dev only!)
        removal_policy=RemovalPolicy.DESTROY
    )

    # LAMBDA FUNCTION
    #-----------------
    # Serverless function that processes contact forms
    lambda_function = lambda_.Function(
        scope, f"{business_unit}-contact-handler",

        # Python 3.12 runtime
        runtime=lambda_.Runtime.PYTHON_3_12,

        # Function to call in my Python file
        handler="construction.contact_handler_construction.contact_handler_construction",

        # Where to find the code
        code=lambda_.Code.from_asset("lambdas"),

        # Environment variables Lambda can access
        environment={
            "TABLE_NAME": table.table_name,
            "FROM_EMAIL": "system@ranjdar-group.com",  # Must verify in SES!
            "TO_EMAIL": "ranjdar.group@gmail.com",  # CHANGE THIS to your email
            "ENVIRONMENT": "dev"
        },

        # 30 seconds should be enough for form processing
        timeout=Duration.seconds(30)
    )

    # PERMISSIONS
    #-------------
    # Lambda needs permission to write to DynamoDB
    table.grant_read_write_data(lambda_function)

    # Lambda needs permission to send emails via SES
    lambda_function.add_to_role_policy(
        iam.PolicyStatement(
            actions=["ses:SendEmail"],  # Only SendEmail, not manage SES
            resources=["*"]  # Could restrict to specific email later
        )
    )

    # API GATEWAY
    #-------------
    # REST API that websites can call
    api = apigateway.RestApi(
        scope, f"{business_unit}-api",
        rest_api_name=f"RanjdarGroup-{business_unit.title()}-API",

        # CORS settings so browser allows cross-domain calls
        default_cors_preflight_options=apigateway.CorsOptions(
            allow_origins=["*"],  # Any website can call (change in production)
            allow_methods=["POST", "OPTIONS"]  # POST for data, OPTIONS for CORS check
        )
    )

    # Create endpoint structure: /api/v1/contact
    api_resource = api.root.add_resource("api")
    v1_resource = api_resource.add_resource("v1")
    contact_resource = v1_resource.add_resource("contact")

    # Connect POST requests to Lambda
    contact_resource.add_method(
        "POST",
        apigateway.LambdaIntegration(lambda_function)
    )

    # Return all created resources in case stack needs references
    return {
        "table": table,
        "lambda": lambda_function,
        "api": api
    }