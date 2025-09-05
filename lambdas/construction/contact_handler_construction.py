"""
Lambda handler for construction business contact form submissions.
Single wrapper around the shared contact form manager.
"""

import os
from typing import Dict, Any
# noinspection PyPackageRequirements
import boto3

from shared.handlers_manager import process_contact_form_submission

# AWS client for DynamoDB
dynamodb = boto3.resource("dynamodb")

#-----------------------------------------------------------
# Environment variables from CDK - static: - CDK sets them
#                                          - Lambda reads them

# DynamoDB table name - CDK creates the table and tells Lambda it's name
TABLE_NAME = os.environ.get("TABLE_NAME")

# Email Lambda will send from (CDK passes this, no default provided to bypass potential silent failing)
FROM_EMAIL = os.environ.get("FROM_EMAIL")

# Recipient for form notifications - my email until other further decisions
TO_EMAIL = os.environ.get("TO_EMAIL")

# Deployment environment - CDK passes dev or prod to control behavior
ENVIRONMENT = os.environ.get("ENVIRONMENT")


# event + context = Lambda required signature param (like __init__(self))
def contact_handler_construction(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Processes construction contact form submission.

    Args:
        event: API Gateway event with form data (dict)
        context: AWS Lambda context - rarely used

    Returns:
        HTTPS response for API Gateway
    """
    _ = context # Lambda requires this parameter
    return process_contact_form_submission(
        event=event,
        business_unit="construction",
        table_name=TABLE_NAME,
        from_email=FROM_EMAIL,
        to_email=TO_EMAIL,
        environment=ENVIRONMENT
    )