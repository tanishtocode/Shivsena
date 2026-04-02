import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.models import User, Complaint, SocialWorkImage
from app import db

auth = Blueprint("auth", __name__)

# ── Constants ────────────────────────────────────────────
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_VIDEOS = {'mp4', 'webm', 'mov'}
MAX_IMAGE_SIZE = (1280, 1280)
IMAGE_QUALITY  = 82


# ── Helpers ──────────────────────────────────────────────
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOS

def get_upload_dir(app):
    path = os.path.join(app.root_path, 'static', 'uploads', 'social_work')
    os.makedirs(path, exist_ok=True)
    return path

def unique_filename(upload_dir, filename):
    base, ext = os.path.splitext(filename)
    final = filename
    counter = 1
    while os.path.exists(os.path.join(upload_dir, final)):
        final = f"{base}_{counter}{ext}"
        counter += 1
    return final

def compress_image(filepath):
    """Resize + compress image in-place using Pillow."""
    try:
        from PIL import Image as PILImage
        img = PILImage.open(filepath)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.thumbnail(MAX_IMAGE_SIZE, PILImage.LANCZOS)
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            img.save(filepath, 'JPEG', quality=IMAGE_QUALITY, optimize=True)
        elif ext == '.webp':
            img.save(filepath, 'WEBP', quality=IMAGE_QUALITY)
        elif ext == '.png':
            img.save(filepath, 'PNG', optimize=True)
    except Exception:
        pass  # Never crash on compression failure


# ── Admin Login ──────────────────────────────────────────
@auth.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash("Login successful!", "success")
            return redirect(url_for("auth.dashboard"))
        flash("Invalid username or password.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("admin/login.html")


# ── Admin Dashboard ──────────────────────────────────────
@auth.route("/admin/dashboard")
@login_required
def dashboard():
    complaints  = Complaint.query.order_by(Complaint.created_at.desc()).all()
    images      = SocialWorkImage.query.order_by(
                      SocialWorkImage.display_order.asc(),
                      SocialWorkImage.created_at.desc()
                  ).all()
    total       = Complaint.query.count()
    pending     = Complaint.query.filter_by(status="Pending").count()
    in_progress = Complaint.query.filter_by(status="In Progress").count()
    resolved    = Complaint.query.filter_by(status="Resolved").count()
    return render_template(
        "admin/dashboard.html",
        complaints=complaints, images=images,
        total=total, pending=pending,
        in_progress=in_progress, resolved=resolved
    )


# ── Update Complaint ─────────────────────────────────────
@auth.route("/admin/update-complaint/<int:complaint_id>", methods=["POST"])
@login_required
def update_complaint(complaint_id):
    complaint  = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get("status")
    admin_note = request.form.get("admin_note", "").strip()
    if new_status not in ["Pending", "In Progress", "Resolved"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("auth.dashboard"))
    complaint.status     = new_status
    complaint.admin_note = admin_note or None
    db.session.commit()
    flash(f"Complaint {complaint.ticket_id} updated.", "success")
    return redirect(url_for("auth.dashboard"))


# ── Logout ───────────────────────────────────────────────
@auth.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


# ── Manage Social Work — List + Multi-Upload ─────────────
@auth.route('/admin/social_work', methods=['GET', 'POST'])
@login_required
def manage_social_work():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        event_date  = request.form.get('event_date', '').strip() or None
        files       = request.files.getlist('image')   # multiple files

        if not files or all(f.filename == '' for f in files):
            flash('Please select at least one file.', 'warning')
            return redirect(url_for('auth.manage_social_work'))

        upload_dir = get_upload_dir(current_app._get_current_object())
        uploaded   = 0

        for file in files:
            if not file or file.filename == '':
                continue

            is_img = allowed_image(file.filename)
            is_vid = allowed_video(file.filename)

            if not is_img and not is_vid:
                flash(f'"{file.filename}" — unsupported format, skipped.', 'warning')
                continue

            filename       = secure_filename(file.filename)
            final_filename = unique_filename(upload_dir, filename)
            final_path     = os.path.join(upload_dir, final_filename)
            file.save(final_path)

            if is_img:
                compress_image(final_path)

            last_order = db.session.query(
                db.func.max(SocialWorkImage.display_order)
            ).scalar() or 0

            new_item = SocialWorkImage(
                image_file    = f'uploads/social_work/{final_filename}',
                title         = title or final_filename,
                description   = description or None,
                event_date    = event_date,
                media_type    = 'video' if is_vid else 'image',
                show_on_slider= False,
                is_featured   = False,
                display_order = last_order + 1
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


# ── Edit Title / Description / Date ─────────────────────
@auth.route('/admin/social_work/edit/<int:image_id>', methods=['POST'])
@login_required
def edit_social_work(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    image.title       = request.form.get('title', '').strip() or image.title
    image.description = request.form.get('description', '').strip() or None
    image.event_date  = request.form.get('event_date', '').strip() or None
    db.session.commit()
    flash('Details updated.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Toggle: Show on Homepage Slider ──────────────────────
@auth.route('/admin/social_work/toggle-slider/<int:image_id>', methods=['POST'])
@login_required
def toggle_slider(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    image.show_on_slider = not image.show_on_slider
    db.session.commit()
    state = 'added to' if image.show_on_slider else 'removed from'
    flash(f'"{image.title}" {state} homepage slider.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Toggle: Featured ─────────────────────────────────────
@auth.route('/admin/social_work/toggle-featured/<int:image_id>', methods=['POST'])
@login_required
def toggle_featured(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    image.is_featured = not image.is_featured
    db.session.commit()
    state = 'marked as' if image.is_featured else 'unmarked from'
    flash(f'"{image.title}" {state} featured.', 'success')
    return redirect(url_for('auth.manage_social_work'))


# ── Move Up ──────────────────────────────────────────────
@auth.route('/admin/social_work/move-up/<int:image_id>', methods=['POST'])
@login_required
def move_up(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    above = SocialWorkImage.query.filter(
        SocialWorkImage.display_order < image.display_order
    ).order_by(SocialWorkImage.display_order.desc()).first()

    if above:
        image.display_order, above.display_order = above.display_order, image.display_order
        db.session.commit()
        flash('Moved up.', 'success')
    else:
        flash('Already at the top.', 'warning')
    return redirect(url_for('auth.manage_social_work'))


# ── Move Down ────────────────────────────────────────────
@auth.route('/admin/social_work/move-down/<int:image_id>', methods=['POST'])
@login_required
def move_down(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    below = SocialWorkImage.query.filter(
        SocialWorkImage.display_order > image.display_order
    ).order_by(SocialWorkImage.display_order.asc()).first()

    if below:
        image.display_order, below.display_order = below.display_order, image.display_order
        db.session.commit()
        flash('Moved down.', 'success')
    else:
        flash('Already at the bottom.', 'warning')
    return redirect(url_for('auth.manage_social_work'))


# ── Set Custom Display Order ─────────────────────────────
@auth.route('/admin/social_work/set-order/<int:image_id>', methods=['POST'])
@login_required
def set_order(image_id):
    image = SocialWorkImage.query.get_or_404(image_id)
    try:
        image.display_order = int(request.form.get('order', image.display_order))
        db.session.commit()
        flash(f'Order set to {image.display_order}.', 'success')
    except (ValueError, TypeError):
        flash('Invalid order value.', 'danger')
    return redirect(url_for('auth.manage_social_work'))


# ── Delete ───────────────────────────────────────────────
@auth.route('/admin/social_work/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_social_work(image_id):
    image      = SocialWorkImage.query.get_or_404(image_id)
    file_path  = os.path.join(current_app.root_path, 'static', image.image_file)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(image)
    db.session.commit()
    flash('File deleted successfully.', 'success')
    return redirect(url_for('auth.manage_social_work'))