"""
Shared Business Website Infrastructure Component (L3 CDK Construct)

    After extensive research and planning, I've decided on a reusable website infrastructure pattern that can in the
    future be used across multiple business units.
    This design allows for
                    consistent deployment and scalable infrastructure for any potential business
                                                                        (construction - current, cosmetics, retail etc.)
                    while maintaining clear separation + cost tracking.

What this construct does:
    - creates an S3 bucket (cloud storage) for website files (HTML, CSS, imgs)
    - sets up CloudFront to serve the website globally with low latency (intent to expand beyond Germany)
    - sets up proper naming conventions for resource organization
    - ensures each business unit can be deployed and managed independently

Why L3 Construct?
    Building my blueprint once for multiple future usages.

Architecture Decision:
    I have a dual goal:
                    meeting the portfolio assignment (CDN, global distribution, IaC)
                    while building the infrastructure for a real future business group

Anca Chiriac, August 25
Cloud Programming Portfolio (DLBSEPCP01_E) + Real Business Infrastructure
"""

from aws_cdk import (
    # S3 = AWS's file storage service
    aws_s3 as s3,

    # CloudFront = AWS's CDN (Content Delivery Network)
    # Makes my website load faster worldwide by copying it to multiple locations
    aws_cloudfront as cloudfront,

    # Origins = where CloudFront gets the website files from (from the S3 bucket)
    aws_cloudfront_origins as origins,

    # RemovalPolicy controls S3 bucket fate when stack is destroyed
    # DESTROY = delete bucket & files (dev/testing - 0 costs)
    # RETAIN = keep bucket and files (production - protects business data)
    RemovalPolicy
)

# Basic building block of CDK
from constructs import Construct

# =================================
# MY CUSTOM WEBSITE CONSTRUCT CLASS
# =================================
class RanjdarGroupWebsite(Construct):
    """
    L3 Construct for creating my website.
    It's intended to work as a template for future business expansions (cosmetics, retail).
    """
    # L3 Construct = high-level, easy to use, lots of defaults set
    # (L1 = raw CloudFormation, L2 = basic CDK, L3 = my custom patterns)

    def __init__(self, scope: Construct, id: str, business_unit: str, org_name: str, **kwargs) -> None:
        """
        :param scope:           the CDK app or stack this belongs to (parent)
        :param id:              unique for each specific instance
        :param business_unit:   starting with construction
        :param org_name:        "ranjdar-group"
        :param kwargs:          other optional param

        Example:
        RanjdarGroupWebsite(self, "website", "construction", "ranjdar-group")
        """
        # Make class inherit all Construct features
        super().__init__(scope, id, **kwargs)

        # ========================
        # STEP 1: Create S3 Bucket
        # ========================
        self.bucket = s3.Bucket(
            # f"{business_unit}-website-bucket" = the CDK ID for this bucket
            self, f"{business_unit}-website-bucket",

            # Bucket name that appears in AWS console, ex.: ranjdar-group-construction-website
            # Must be globally unique across ALL AWS customers worldwide
            bucket_name=f"{org_name}-{business_unit}-website",

            # -------------------------------
            # STATIC WEBSITE HOSTING SETTINGS
            # S3 bucket = website, not just file storage

            # When someone visits my domain, show this file:
            website_index_document="index.html",

            # When someone visits a page that doesn't exist, show this:
            website_error_document="error.html",

            # -------------------------------
            # CLEANUP SETTINGS
            # Removal.Policy.DESTROY = Delete the bucket
            # Removal.Policy.RETAIN = Keep the bucket (use for production)
            removal_policy=RemovalPolicy.DESTROY, # For dev only

            # auto_delete_objects=True means del all files in the bucket when destroying
            # Without this CDK can't delete non-empty buckets
            auto_delete_objects=True # For dev only
        )

        # =============================================
        # STEP 2: Create CLOUD FRONT DISTRIBUTION (CDN)
        # =============================================
        # CloudFront = Content Delivery Network
        #
        # - copies my website to multiple locations worldwide
        # - users get files from nearest location = fast
        # - provide HTTPS (secure connection) for free
        # - protects against DDoS attacks

        self.distribution = cloudfront.Distribution(
            # CDK ID for this distribution
            self, f"{business_unit}-distribution",

            # DEFAULT BEHAVIOR
            # "Behavior" = Rules for how CloudFront handles requests
            # "Default" = Rules for all requests (unless I add specific paths)
            default_behavior=cloudfront.BehaviorOptions(
                # ORIGIN = where CloudFront gets the files
                # S3Origin = get files from an S3 bucket
                origin=origins.S3Origin(self.bucket) # Tells CloudFront to get files from my bucket above
            ),

            # COMMENT = Description in my AWS Console
            # helps me identify this distribution later
            comment=f"CDN for {business_unit} business unit",

            # Hardcode the PriceClass since my initial deployment is in EU only (and the foreseeable future)
            price_class=cloudfront.PriceClass.PRICE_CLASS_100 # EU, US, Canada only
        )