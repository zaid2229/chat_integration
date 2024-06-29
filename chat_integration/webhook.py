shhimport frappe
from frappe.utils import now_datetime
import re

@frappe.whitelist(allow_guest=True)
def receive_message():
    # Log incoming data for debugging
    frappe.log_error(frappe.as_json(frappe.local.form_dict), "Webhook Data")
    
    # Check for 'text' in POST data
    if 'text' in frappe.local.form_dict:
        message = frappe.local.form_dict.get('text')
        email = extract_email(message)
        if email:
            create_task(email, message)
        return {"status": "success", "message": "Task created successfully"}
    
    # Check for 'email' and 'message' in GET query parameters
    email = frappe.local.form_dict.get('email')
    message = frappe.local.form_dict.get('message')
    if email and message:
        create_task(email, message)
        return {"status": "success", "message": "Task created successfully"}
    
    return {"status": "error", "message": "No message found"}

def extract_email(text):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_regex, text)
    return match.group(0) if match else None

def create_task(email, message):
    doc = frappe.get_doc({
        "doctype": "Task",
        "subject": "Task from Google Chat",
        "description": message,
        "assigned_by": email,
        "expected_end_date": now_datetime()
    })
    doc.insert()
    frappe.db.commit()

