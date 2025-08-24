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
    - sets up CloudFront to serve the website globally with low latency (intent to expand outside Germany)
    - sets up proper naming conventions for resource organization
    - ensures each business unit can be deployed and managed independently

Why L3 Construct?
    Building my blueprint once for multiple future usages.

Architecture Decision:
    I have a dual goal:
                    meeting the portfolio assignment (CDN, global distribution, IaC)
                    while building real infrastructure for a real future business group.

Anca Chiriac, August 25
Cloud Programming Portfolio (DLBSEPCP01_E) + Real Business Infrastructure
"""