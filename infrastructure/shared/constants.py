"""
Shared constants and helper functions for AWS CDK infrastructure.
Keeps everything consistent across all business units.
"""

from typing import Dict

def get_mandatory_tags(business_unit: str, country: str = "DE", environment: str = "dev") -> Dict[str, str]:
    """
    Generates tags for all AWS resources in the business group.

    Tags help track costs and filter resources in AWS Console.
    Every S3 bucket, Lambda function, CloudFront distribution gets these tags.
    AWS then tracks costs per tag in Cost Explorer.

    Args:
        business_unit: construction, retail, etc.
        country: Country code for operations ("DE", "RO", etc.)
        environment: dev, prod

    Returns:
        Dictionary of tags to apply for AWS resources
    """
    return {
        # Parent organization name - shows up in AWS billing reports
        "Organization": "RanjdarGroup",

        # Which business this belongs to - most important for cost tracking
        "BusinessUnit": business_unit,

        # Country for multinational operations and tax compliance
        "Country": country,

        # Helps separate current and future dev vs prod costs
        "Environment": environment,

        # For university assignment - remove or change to "Production" after passing the module
        "Project": "Portfolio",

        # Accounting code - each business/country gets unique code (increment if needed in the future)
        "CostCenter": f"{business_unit}-{country.lower()}-001"
    }


def get_resource_names(business_unit: str, resource_type: str, country: str = "") -> str:
    """
    Creates consistent AWS resource names.

    S3 buckets need globally unique names across ALL AWS accounts.
    This pattern prevents conflicts and makes resources easier to find.

    Args:
        business_unit: construction, retail, etc.
        resource_type: S3 bucket, API Gateway, DynamoDB table
        country: DE, RO, etc.

    Returns:
        Formatted resource name in lowercase.

    Examples:
        ranjdargroup-construction-website (S3 Bucket)
        ranjdargroup-construction-de-api (API Gateway)
        ranjdargroup-retail-ro-dynamodb (DynamoDB table)
    """
    parts = ["ranjdargroup", business_unit] # Hardcore org name - lowercase version of Organization tag
    if country:
        parts.append(country.lower())
    parts.append(resource_type)

    # AWS requires lowercase for most resource names
    return "-".join(parts).lower()


def get_subdomain_mapping() -> Dict[str, list]:
    """
    Maps business units to their subdomains.

    Used by CloudFront and Route 53 to route traffic.
    Makes it easy to add new businesses without changing code.
    Mapping follows this pattern: German, English, Romanian

    Returns:
        Dictionary mapping business_unit to subdomain prefix.
    """
    # Add more as needed in the future
    return {
        "construction": ["bau", "construction", "constructii"], # DE, EN, RO
        "recruitment": ["bewerben", "recruitment", "angajare"]
    }


def get_business_email(business_unit: str) -> str:
    """
    Generates business email addresses.

    Each business gets its own info@ email via SES.
    Uses English subdomain for each business.

    Args:
        business_unit: business unit name in English

    Returns:
        Email address string.
    """
    subdomain_map = get_subdomain_mapping()
    subdomain = subdomain_map.get(business_unit, [business_unit])

    # Retrieve EN subdomain
    en_subdomain = subdomain[1]

    # Hardcode domain
    return f"info@{en_subdomain}.ranjdar-group.com"


def is_prod_environment(environment: str) -> bool:
    """
    Checks if we're in production.

    Critical for RemovalPolicy - prod should NEVER auto-delete.
    Propagates to retention periods, backup schedules, and alerting.

    Args:
        environment: dev, prod

    Returns:
        True if production environment, False otherwise.
    """
    return environment.lower() == "prod"


def get_retention_days(environment: str) -> int:
    """
    Defines how long to keep logs and backups.

    CloudWatch logs cost 0,03/GB
    Dev = 7 days (saves me money), Prod = 90 days (compliance)

    Args:
        environment: dev, prod

    Returns:
        The number of days to retain logs/backups.
    """
    if is_prod_environment(environment):
        return 90
    return 7 # Else dev