from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Complaint
from datetime import datetime
import random

complaints = Blueprint("complaints", __name__)

# Submit Complaint
@complaints.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        category = request.form.get("category")
        complaint_location = request.form.get("complaint_location")
        description = request.form.get("description")
        priority = request.form.get("priority")
        photo = request.files.get("photo")

        # Generate Ticket ID
        ticket_id = f"JAN-{datetime.now().year}-{random.randint(1000, 9999)}"

        # Photo filename (optional)
        photo_filename = photo.filename if photo and photo.filename else None

        new_complaint = Complaint(
            ticket_id=ticket_id,
            name=fullname,
            phone=phone,
            email=email,
            address=address,
            category=category,
            location=complaint_location,
            description=description,
            priority=priority.capitalize() if priority else "Medium",
            status="Pending",
            photo=photo_filename
        )

        db.session.add(new_complaint)
        db.session.commit()

        flash(f"Complaint submitted successfully! Your Ticket ID is {ticket_id}", "success")
        return redirect(url_for("complaints.submit"))

    return render_template("complaints/submit.html")


# Track Complaint
@complaints.route("/track", methods=["GET", "POST"])
def track():
    complaint = None

    if request.method == "POST":
        ticket_id = request.form.get("ticket_id", "").strip()

        if ticket_id:
            complaint = Complaint.query.filter_by(ticket_id=ticket_id).first()

            if not complaint:
                flash("No complaint found with this Ticket ID.", "danger")
        else:
            flash("Please enter a Ticket ID.", "danger")

    return render_template("complaints/track.html", complaint=complaint)