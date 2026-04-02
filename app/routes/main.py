from flask import Blueprint, render_template
from app.models import SocialWorkImage
from . import main

main = Blueprint("main", __name__)

@main.route('/')
def index():
    social_works = SocialWorkImage.query.order_by(SocialWorkImage.created_at.desc()).all()
    return render_template('index.html', social_works=social_works)

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/contact")
def contact():
    return render_template("contact.html")

@main.route('/helplines')
def helplines():
    return render_template('helplines.html')

@main.route('/social-work')
def social_work():
    social_works = SocialWorkImage.query.order_by(SocialWorkImage.created_at.desc()).all()
    return render_template('social_work.html', social_works=social_works)