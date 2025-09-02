from aws_cdk import aws_s3_deployment as s3deploy
from constructs import Construct

from infrastructure.shared.config.constants import generate_api_config


def deploy_website(scope: Construct, business_unit: str, bucket, api_url: str) -> None:
    """
    Deploys website files and generates API config for any business unit.
    Called after API creation = when I have urls, not CDK tokens.

    Args:
        scope: CDK construct scope (the stack)
        business_unit:
        bucket: S3 bucket from website construct
        api_url: API Gateway URL after creation
    """
    # Generate config
    generate_api_config(api_url, business_unit)

    # Deploy all website files including generated config
    s3deploy.BucketDeployment(
        scope, f"{business_unit}-website-deployment",
        sources=[s3deploy.Source.asset(f"website/{business_unit}")],
        destination_bucket=bucket
    )