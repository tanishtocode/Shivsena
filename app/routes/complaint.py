from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Complaint
from werkzeug.utils import secure_filename
from datetime import datetime
import random
import string
import os

complaints = Blueprint("complaints", __name__)

# SECURITY FIX: allowed extensions for complaint photo upload
ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def allowed_photo(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS
    )

def generate_ticket_id():
    """
    BUG FIX: old random.randint(1000,9999) could collide.
    Now uses 6 random alphanumeric chars — collision probability is negligible.
    """
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"JAN-{datetime.now().year}-{suffix}"


# Submit Complaint
@complaints.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        fullname           = request.form.get("fullname", "").strip()
        phone              = request.form.get("phone", "").strip()
        email              = request.form.get("email", "").strip() or None
        address            = request.form.get("address", "").strip()
        category           = request.form.get("category", "").strip()
        complaint_location = request.form.get("complaint_location", "").strip()
        description        = request.form.get("description", "").strip()
        priority           = request.form.get("priority", "medium").strip()
        photo              = request.files.get("photo")

        # Basic server-side validation
        if not all([fullname, phone, address, category, complaint_location, description]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("complaints.submit"))

        # Generate collision-safe Ticket ID
        ticket_id = generate_ticket_id()
        # Ensure uniqueness (retry if somehow duplicate exists)
        while Complaint.query.filter_by(ticket_id=ticket_id).first():
            ticket_id = generate_ticket_id()

        # BUG FIX: actually save the photo file to disk + validate type
        photo_filename = None
        if photo and photo.filename:
            if not allowed_photo(photo.filename):
                flash("Only JPG, PNG, or WEBP images are allowed for photo.", "danger")
                return redirect(url_for("complaints.submit"))

            filename       = secure_filename(photo.filename)
            upload_dir     = os.path.join(current_app.root_path, 'static', 'uploads', 'complaints')
            os.makedirs(upload_dir, exist_ok=True)
            save_path      = os.path.join(upload_dir, filename)
            photo.save(save_path)
            photo_filename = f'uploads/complaints/{filename}'

        new_complaint = Complaint(
            ticket_id   = ticket_id,
            name        = fullname,
            phone       = phone,
            email       = email,
            address     = address,
            category    = category,
            location    = complaint_location,
            description = description,
            priority    = priority.capitalize(),
            status      = "Pending",
            photo       = photo_filename
        )

        db.session.add(new_complaint)
        db.session.commit()

        flash(f"Complaint submitted! Your Ticket ID is {ticket_id} — save it to track your complaint.", "success")
        return redirect(url_for("complaints.submit"))

    return render_template("complaints/submit.html")


# Track Complaint
@complaints.route("/track", methods=["GET", "POST"])
def track():
    complaint = None

    if request.method == "POST":
        ticket_id = request.form.get("ticket_id", "").strip().upper()

        if ticket_id:
            complaint = Complaint.query.filter_by(ticket_id=ticket_id).first()
            if not complaint:
                flash("No complaint found with this Ticket ID.", "danger")
        else:
            flash("Please enter a Ticket ID.", "danger")

    return render_template("complaints/track.html", complaint=complaint)