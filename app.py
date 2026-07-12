

import os
import csv
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from flask import Flask, request, render_template, redirect, url_for, flash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"csv"}
ALLOWED_TEMPLATE_EXT = {"html", "htm", "txt"}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "degistir-bu-anahtari")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SENDER_NAME = os.environ.get("SENDER_NAME", "Information")

SEND_DELAY_SECONDS = float(os.environ.get("SEND_DELAY_SECONDS", "1.5"))

PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")

def allowed_file(filename: str, allowed_set: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set
def read_recipients(csv_path: str):
    recipients = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "email" not in [h.strip().lower() for h in reader.fieldnames]:
            raise ValueError("CSV dosyasında 'email' sütunu bulunamadı.")
        for row in reader:
            clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
            recipients.append(clean_row)
    return recipients
def render_template_string(template_str: str, variables: dict) -> str:
    def replace(match):
        key = match.group(1)
        return str(variables.get(key, ""))
    return PLACEHOLDER_PATTERN.sub(replace, template_str)
def find_placeholders(template_str: str):
    return sorted(set(PLACEHOLDER_PATTERN.findall(template_str)))
def send_single_mail(to_email: str, subject: str, body: str, is_html: bool = True):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    mime_type = "html" if is_html else "plain"
    msg.attach(MIMEText(body, mime_type, "utf-8"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
def send_bulk_mails(recipients: list, subject_template: str, body_template: str,
                     is_html: bool = True, delay: float = SEND_DELAY_SECONDS):
    results = []
    for row in recipients:
        to_email = row.get("email", "").strip()
        if not to_email:
            results.append({"email": "(bos)", "status": "atlandi", "hata": "email alani bos"})
            continue
        personalized_subject = render_template_string(subject_template, row)
        personalized_body = render_template_string(body_template, row)
        try:
            send_single_mail(to_email, personalized_subject, personalized_body, is_html)
            results.append({"email": to_email, "status": "basarili", "hata": ""})
        except Exception as e:
            results.append({"email": to_email, "status": "basarisiz", "hata": str(e)})
        time.sleep(delay)
    return results
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
@app.route("/preview", methods=["POST"])
def preview():
    csv_file = request.files.get("csv_file")
    template_file = request.files.get("template_file")
    subject_template = request.form.get("subject", "")
    if not csv_file or not allowed_file(csv_file.filename, ALLOWED_EXTENSIONS):
        flash("Geçerli bir .csv dosyası yükleyin.")
        return redirect(url_for("index"))
    if not template_file or not allowed_file(template_file.filename, ALLOWED_TEMPLATE_EXT):
        flash("Geçerli bir .html/.htm/.txt şablon dosyası yükleyin.")
        return redirect(url_for("index"))
    csv_path = os.path.join(app.config["UPLOAD_FOLDER"], csv_file.filename)
    csv_file.save(csv_path)
    template_str = template_file.read().decode("utf-8")
    is_html = template_file.filename.lower().endswith((".html", ".htm"))
    recipients = read_recipients(csv_path)
    if not recipients:
        flash("CSV dosyasında hiç alıcı bulunamadı.")
        return redirect(url_for("index"))
    used_placeholders = find_placeholders(template_str)
    sample = recipients[0]
    preview_subject = render_template_string(subject_template, sample)
    preview_body = render_template_string(template_str, sample)
    return render_template(
        "preview.html",
        preview_subject=preview_subject,
        preview_body=preview_body,
        is_html=is_html,
        total_recipients=len(recipients),
        used_placeholders=used_placeholders,
        csv_filename=csv_file.filename,
        subject_template=subject_template,
        template_str=template_str,
        template_is_html=is_html,
    )
@app.route("/send", methods=["POST"])
def send():
    csv_filename = request.form.get("csv_filename")
    subject_template = request.form.get("subject_template", "")
    body_template = request.form.get("body_template", "")
    is_html = request.form.get("is_html") == "True"
    csv_path = os.path.join(app.config["UPLOAD_FOLDER"], csv_filename)
    if not os.path.exists(csv_path):
        flash("CSV dosyası bulunamadı, lütfen tekrar yükleyin.")
        return redirect(url_for("index"))
    if not SMTP_USER or not SMTP_PASS:
        flash("SMTP_USER / SMTP_PASS ortam değişkenleri ayarlanmamış!")
        return redirect(url_for("index"))
    recipients = read_recipients(csv_path)
    results = send_bulk_mails(recipients, subject_template, body_template, is_html)
    success_count = sum(1 for r in results if r["status"] == "basarili")
    fail_count = sum(1 for r in results if r["status"] == "basarisiz")
    log_line = f"[{datetime.now()}] Gonderim tamamlandi: {success_count} basarili, {fail_count} basarisiz\n"
    with open(os.path.join(UPLOAD_FOLDER, "gonderim_log.txt"), "a", encoding="utf-8") as logf:
        logf.write(log_line)
    return render_template("result.html", results=results,
                            success_count=success_count, fail_count=fail_count)
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
