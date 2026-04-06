from flask import Blueprint, render_template
from app.models import SocialWorkImage

# BUG FIX: removed "from . import main" which was importing itself before it existed
# That line caused a startup crash — it's simply not needed here
main = Blueprint("main", __name__)


@main.route('/')
def index():
    # Only fetch images that are set to show on slider, ordered correctly
    social_works = SocialWorkImage.query.filter_by(show_on_slider=True).order_by(
        SocialWorkImage.display_order.asc()
    ).all()
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
    social_works = SocialWorkImage.query.order_by(
        SocialWorkImage.display_order.asc(),
        SocialWorkImage.created_at.desc()
    ).all()
    return render_template('social_work.html', social_works=social_works)