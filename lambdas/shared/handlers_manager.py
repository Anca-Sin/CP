"""
Shared handler manager functions for all business units.
Single entry point for processing any contact form submissions.
"""

import json
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

# noinspection PyPackageRequirements
import boto3

from shared.utils import sanitize_input, determine_language_from_domain, create_cors_response

dynamodb = boto3.resource("dynamodb")

# Simple Email Service client
# Handles all email operations through the Frankfurt region for GDPR (= General Data Protection Regulation)
# EU laws require businesses to protect EU citizens' personal data and keep it within EU borders
# .client = low-lvl, direct API mapping, more control
ses = boto3.client("ses", region_name="eu-central-1")


def process_contact_form_submission(
        event: Dict[str, Any],
        business_unit: str,
        table_name: str,
        from_email: str,
        to_email: str,
        environment: str = "dev"
) -> Dict[str, Any]:
    """
    Complete contact form processing for any business unit.
    Handles:
    - validation
    - storage
    - email
    - multi-language responses

    Args:
        event: API Gateway event with form data
        business_unit: construction, retail, etc.
        table_name: DynamoDB table name
        from_email: verified SES sender
        to_email: recipient email
        environment: dev or prod

    Returns:
        API Gateway response with CORS headers
    """
    # Determine language from subdomain origin
    origin = event.get("headers", {}).get("origin", "")
    language = determine_language_from_domain(origin)

    # Response message in all languages
    messages = {
        "EN": {
            "success": "Contact form submitted successfully!",
            "missing_fields": "Missing mandatory fields",
            "server_error": "Internal server error"
        },

        "DE": {
            "success": "Das Kontaktformular wurde erfolgreich abgeschickt!",
            "missing_fields": "Pflichtfelder fehlen",
            "server_error": "Serverfehler"
        },

        "RO": {
            "success": "Formularul de contact a fost trimis cu succes!",
            "missing_fields": "Câmpuri obligatorii lipsă",
            "server_error": "Eroare internă"
        }
    }

    response_msg = messages.get(language, messages["EN"]) # default to english

    try:
        # Parse form data
        body = json.loads(event.get("body", "{}"))

        # Extract mandatory fields
        contact_person = body.get("contact_person", "").strip()
        email = body.get("email", "").strip()
        phone = body.get("phone", "").strip()
        message = sanitize_input(body.get("message", "").strip())

        # Validate required fields
        if not all([contact_person, email, phone, message]):
            return create_cors_response(400, {"error": response_msg["missing_fields"]})

        # Extract optional fields
        company = body.get("company", "").strip()
        project_type = body.get("project_type", "").strip()
        timeline = body.get("timeline", "").strip()
        units_needed = body.get("units_needed", "").strip()

        # Generate IDs
        contact_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create DynamoDB item
        item = {
            "pk": f"BU#{business_unit.upper()}",
            "sk": f"CONTACT#{timestamp}#{contact_id}",
            "contact_id": contact_id,
            "business_unit": business_unit,
            "timestamp": timestamp,
            "environment": environment,
            "status": "new",
            "contact_person": contact_person,
            "email": email,
            "phone": phone,
            "message": message,
            "company": company,
            "project_type": project_type,
            "timeline": timeline,
            "units_needed": units_needed,
            "source_domain": origin
        }

        # Remove empty strings to save storage
        item = {k: v for k, v in item.items() if v}

        # Save to DynamoDB
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)

        # Format email based on language
        email_subject, email_body = format_email_content(
            business_unit, company, contact_person, email, phone,
            message, project_type, timeline, units_needed,
            timestamp, language
        )

        # Try to send email but don't fail if it doesn't work
        try:
            ses.send_email(
                Source=from_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": email_subject, "Charset": "UTF-8"},
                    "Body": {"Text": {"Data": email_body, "Charset": "UTF-8"}}
                }
            )
        except Exception as e:
            print(f"Email failed for {contact_id}: {str(e)}")
            print("Data saved successfully to DynamoDB")

        # Success response
        return create_cors_response(200, {
            "message": response_msg["success"],
            "contact_id": contact_id
        })

    except Exception as e:
        print(f"Error processing contact form: {str(e)}")
        return create_cors_response(500, {"error": messages["server_error"]})


def format_email_content(
        business_unit: str, company: str, contact_person: str,
        email: str, phone: str, message: str, project_type: str,
        timeline: str, units_needed: str, timestamp: str, language: str
) -> tuple[str, str]:
    """
    Format email notification in appropriate language.
    """
    templates = {
        "DE": {
            "subject": f"Neue Anfrage: {business_unit}",
            "greeting": f"Neue Anfrage eingegangen:",
            "labels": {
                "company": "Firma",
                "contact": "Kontakt Person",
                "email": "Email",
                "phone": "Tel.",
                "project": "Projekttyp",
                "timeline": "Zeitplan",
                "units": "Benötigte Einheiten",
                "message": "Nachricht",
                "timestamp": "Zeitstempel",
                "not_specified": "Nicht angegeben"
            }
        },
        "EN": {
            "subject": f"New inquiry: {business_unit}",
            "greeting": f"New inquiry received:",
            "labels": {
                "company": "Company",
                "contact": "Contact Person",
                "email": "Email",
                "phone": "Phone",
                "project": "Project Type",
                "timeline": "Timeline",
                "units": "Units Needed",
                "message": "Message",
                "timestamp": "Timestamp",
                "not_specified": "Not specified"
            }
        },
        "RO": {
            "subject": f"Cerere nouă: {business_unit}",
            "greeting": f"Cerere nouă primită:",
            "labels": {
                "company": "Companie",
                "contact": "Persoană de contact",
                "email": "Email",
                "phone": "Telefon",
                "project": "Tip proiect",
                "timeline": "Termen",
                "units": "Unități necesare",
                "message": "Mesaj",
                "timestamp": "Marcaj temporal",
                "not_specified": "Nespecificat"
            }
        }
    }

    t = templates.get(language, templates["DE"])
    l = t["labels"]

    body_parts = [
        t["greeting"],
        "",
        f"{l['company']}: {company}",
        f"{l['contact']}: {contact_person}",
        f"{l['email']}: {email}",
        f"{l['phone']}: {phone}",
        "",
        f"{l['project']}: {project_type or l['not_specified']}",
        f"{l['timeline']}: {timeline or l['not_specified']}",
    ]

    if units_needed:
        body_parts.append(f"{l['units']}: {units_needed}")

    body_parts.extend([
        "",
        f"{l['message']}:",
        message,
        "",
        "---",
        f"{l['timestamp']}: {timestamp}"
    ])

    return t["subject"], "\n".join(body_parts)