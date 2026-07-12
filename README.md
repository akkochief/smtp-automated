# SMTP Automated Email Sender

A small web application that uses Flask + SMTP to send personalized emails
to each recipient from a CSV list, replacing placeholders like `{name}`,
`{x}`, `{y}`, `{z}` with actual values.

## Files

- `app.py` — Flask application and email sending logic
- `templates/index.html` — file upload form
- `templates/preview.html` — preview before sending
- `templates/result.html` — delivery results report
- `example.csv` — sample recipient list
- `example.html` — sample email template


## Installation

```bash
cd mailapp
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
