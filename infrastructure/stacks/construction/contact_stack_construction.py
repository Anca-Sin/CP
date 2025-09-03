"""
CDK Stack for my construction website portfolio project.
Organized as:
                    - shared contact_form_infrastructure manager
                                +
                    - wrapper for the construction business
                                =
                      My clear mental picture of CDK.

This stack creates everything I need for the AWS assignment. I'm building a real website for a concrete construction
family business but making sure it checks all the portfolio requirements.

Main components:
- S3 + CloudFront
- Lambda for simple contact form
- API Gateway to connect frontend to Lambda
- DynamoDB for storing form submissions
- Needed IAM permissions

Important for testing: SES email notification won't work for the tutor unless he configures it, but I handle this error
                       so Lambda doesn't crash (see contact_handler_construction.py)
                       Data still saves to DynamoDB even if the email fails

Future plan: my project is structured to expand businesses later (cosmetics, retail, etc.) - why the business_unit tags

Anca Chiriac
Cloud Programming_DLBSEPCP01_E_CF Portfolio
"""

from aws_cdk import (
    Stack,
    Tags,
    CfnOutput
)
from constructs import Construct
from infrastructure.shared.constructs.website_construct import RanjdarGroupWebsite
from infrastructure.shared.managers.contact_form_infrastructure import create_contact_form_infrastructure
from infrastructure.shared.config.constants import get_mandatory_tags, generate_api_config, deploy_bucket


class ContactConstructionStack(Stack):
    """
    My main CDK stack that creates everything for the portfolio.
    It inherits Stack to get all CDK stack functionality.
    This combines S3/CloudFront website + Lambda + API Gateway + DynamoDB.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        # Calling parent class constructor for inheritance to work properly
        super().__init__(scope, construct_id, **kwargs)

        # STATIC WEBSITE (S3 + CloudFront)
        #----------------------------------
        # Using my L3 construct from website_construct.py
        self.website = RanjdarGroupWebsite(
            self,
            "construction-website",
            business_unit="construction",
            org_name="ranjdargroup"
        )

        # CONTACT FORM INFRASTRUCTURE
        #-----------------------------
        # Create all contact form resources with one function call
        # Returns dict with table, lambda, and api references
        contact_infra = create_contact_form_infrastructure(self, "construction")

        # Store references on stack for potential future use
        self.contact_table = contact_infra["table"]
        self.contact_lambda = contact_infra["lambda"]
        self.api = contact_infra["api"]

        # Generate config with resolved URL
        generate_api_config(self.api.url, "construction")

        # Deploy files
        deploy_bucket(self, "construction", self.website.bucket)

        # TAGS FOR COST TRACKING
        #------------------------
        tags = get_mandatory_tags("construction", "EN", "dev")
        for key, value in tags.items():
            Tags.of(self).add(key, value)

        # OUTPUTS (shown after deploy)
        #------------------------------
        CfnOutput(self, "WebsiteURL",
            value=f"https://{self.website.distribution.distribution_domain_name}",
            description="CloudFront URL for website")

        CfnOutput(self, "ApiURL",
            value=self.api.url,
            description="API Gateway URL for contact form")

        CfnOutput(self, "BucketName",
            value=self.website.bucket.bucket_name,
            description="S3 bucket name for uploading HTML")