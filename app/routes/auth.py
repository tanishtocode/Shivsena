import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User, Complaint, SocialWorkImage
from app import db

import cloudinary
import cloudinary.uploader

auth = Blueprint("auth", __name__)

# ── Constants ────────────────────────────────────────────
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_VIDEOS = {'mp4', 'webm', 'mov'}


# ── Helpers ──────────────────────────────────────────────
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOS


# ── Admin Login ──────────────────────────────────────────
@auth.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash("Login successful!", "success")
            return redirect(url_for("auth.dashboard"))

        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("admin/login.html")


# ── Dashboard ────────────────────────────────────────────
@auth.route("/admin/dashboard")
@login_required
def dashboard():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    images = SocialWorkImage.query.order_by(
        SocialWorkImage.display_order.asc(),
        SocialWorkImage.created_at.desc()
    ).all()

    return render_template(
        "admin/dashboard.html",
        complaints=complaints,
        images=images,
        total=Complaint.query.count(),
        pending=Complaint.query.filter_by(status="Pending").count(),
        in_progress=Complaint.query.filter_by(status="In Progress").count(),
        resolved=Complaint.query.filter_by(status="Resolved").count()
    )


# ── Logout ───────────────────────────────────────────────
@auth.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


# ── Manage Social Work (UPLOAD) ──────────────────────────
@auth.route('/admin/social_work', methods=['GET', 'POST'])
@login_required
def manage_social_work():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        event_date = request.form.get('event_date', '').strip() or None
        files = request.files.getlist('image')

        if not files or all(f.filename == '' for f in files):
            flash('Please select at least one file.', 'warning')
            return redirect(url_for('auth.manage_social_work'))

        uploaded = 0

        for file in files:
            if not file or file.filename == '':
                continue

            is_img = allowed_image(file.filename)
            is_vid = allowed_video(file.filename)

            if not is_img and not is_vid:
                flash(f'"{file.filename}" — unsupported format, skipped.', 'warning')
                continue

            try:
                result = cloudinary.uploader.upload(
                    file,
                    folder="shivsetu/social_work",
                    resource_type="auto"
                )

                file_url = result.get("secure_url")

            except Exception:
                flash(f"Upload failed for {file.filename}", "danger")
                continue

            last_order = db.session.query(
                db.func.max(SocialWorkImage.display_order)
            ).scalar() or 0

            new_item = SocialWorkImage(
                image_file=file_url,
                title=title or file.filename,
                description=description or None,
                event_date=event_date,
                media_type='video' if is_vid else 'image',
                show_on_slider=False,
                is_featured=False,
                display_order=last_order + 1
            )

            db.session.add(new_item)
            uploaded += 1

        if uploaded:
            db.session.commit()
            flash(f'{uploaded} file(s) uploaded successfully!', 'success')

        return redirect(url_for('auth.manage_social_work'))

    images = SocialWorkImage.query.order_by(
        SocialWorkImage.display_order.asc(),
        SocialWorkImage.created_at.desc()
    ).all()

    return render_template('admin/manage_social_work.html', images=images)


# ── Edit ─────────────────────────────────────────────────
@auth.route('/admin/social_work/edit/<int:image_id>', methods=['POST'])
@login_required
def edit_social_work(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)

    image.title = request.form.get('title', '').strip() or image.title
    image.description = request.form.get('description', '').strip() or None
    image.event_date = request.form.get('event_date', '').strip() or None

    db.session.commit()
    flash('Details updated.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Toggle Slider ────────────────────────────────────────
@auth.route('/admin/social_work/toggle-slider/<int:image_id>', methods=['POST'])
@login_required
def toggle_slider(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    image.show_on_slider = not image.show_on_slider
    db.session.commit()

    flash('Slider updated.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Toggle Featured ──────────────────────────────────────
@auth.route('/admin/social_work/toggle-featured/<int:image_id>', methods=['POST'])
@login_required
def toggle_featured(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    image.is_featured = not image.is_featured
    db.session.commit()

    flash('Featured updated.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Delete (Cloudinary) ──────────────────────────────────
@auth.route('/admin/social_work/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_social_work(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)

    try:
        # Extract public_id from URL
        url_parts = image.image_file.split('/')
        public_id = "/".join(url_parts[-3:]).split('.')[0]

        cloudinary.uploader.destroy(public_id, resource_type="image")
        cloudinary.uploader.destroy(public_id, resource_type="video")

    except Exception:
        pass

    db.session.delete(image)
    db.session.commit()

    flash('File deleted successfully.', 'success')
    return redirect(url_for('auth.manage_social_work'))