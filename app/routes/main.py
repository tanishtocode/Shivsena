from flask import Blueprint, render_template, session, redirect, request, url_for
from app.models import SocialWorkImage

# ✅ ALWAYS DEFINE BLUEPRINT FIRST
main = Blueprint("main", __name__)


# 🌐 Language Switch Route
@main.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'mr']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))


# 🏠 Home Page
@main.route('/')
def index():
    social_works = SocialWorkImage.query.filter_by(show_on_slider=True).order_by(
        SocialWorkImage.display_order.asc()
    ).all()

    return render_template('index.html', social_works=social_works)


# 📄 About Page
@main.route("/about")
def about():
    return render_template("about.html")


# 📞 Contact Page
@main.route("/contact")
def contact():
    return render_template("contact.html")


# 🚨 Helplines Page
@main.route('/helplines')
def helplines():
    return render_template('helplines.html')


# 🖼️ Social Work Page
@main.route('/social-work')
def social_work():
    social_works = SocialWorkImage.query.order_by(
        SocialWorkImage.display_order.asc(),
        SocialWorkImage.created_at.desc()
    ).all()

    return render_template('social_work.html', social_works=social_works)