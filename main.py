from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from dotenv import load_dotenv
import os
# Import your forms from the forms.py
from forms import CreatePostForm, RegistrationForm, LoginForm, CommentForm

# Load environmental variables
load_dotenv()
email_id = os.getenv("EMAIL_ID")
password = os.getenv("PASSWORD")


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Adding profile images to comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None
                    )



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bamboo-blogs.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    db.create_all()

# Only Admin Decorative
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template("401.html")
        if current_user.id != 1:
            return render_template("403.html")
        return f(*args, **kwargs)
    return decorated_function


def initialize_data():
    # Check if users and admin already exists
    admin_user = db.session.execute(db.select(User).where(User.email == "admin@gmail.com")).scalar()
    if not admin_user:
        hashed_password = generate_password_hash('password', method='pbkdf2:sha256', salt_length=8)
        admin_user = User(
            name="Admin",
            email="admin@gmail.com",
            password=hashed_password
        )
        db.session.add(admin_user)
        db.session.commit()
    
    user1 = db.session.execute(db.select(User).where(User.email == "user1@gmail.com")).scalar()
    if not user1:
        hashed_password = generate_password_hash('password', method='pbkdf2:sha256', salt_length=8)
        user1 = User(
            name="User 1",
            email="user1@gmail.com",
            password=hashed_password
        )
        db.session.add(user1)
        db.session.commit()

    # Check if the blog post exists
    existing_post = db.session.execute(db.select(BlogPost)).scalar()
    if not existing_post:
        new_post = BlogPost(
            title="Beyond the Stars: Humanity’s Quest to Explore the Cosmos",
            subtitle="Charting Our Journey from the First Telescope to Interstellar Ambitions",
            body = """
<p>
  <strong>Space</strong> has always fascinated humankind, stirring a profound curiosity about what lies beyond our blue planet.
  From the early astronomers who meticulously mapped the stars to the modern-day engineers designing spacecraft capable of reaching the edge of our solar system,
  <em>our journey into the cosmos is a testament to human ingenuity and wonder.</em>
</p>

<p>
  The story begins with <strong>Galileo’s telescope</strong>, a simple instrument that forever changed our understanding of the universe.
  As lenses improved and scientific methods advanced, we discovered planets, moons, and countless celestial phenomena that challenged our place in the cosmos.
</p>

<p style="margin-top:1em;">
  The 20th century ushered in the <strong>Space Age</strong>, marked by the launch of <em>Sputnik</em> and the historic <strong>Apollo 11 mission</strong>,
  which saw Neil Armstrong set foot on the Moon, whispering words that would echo through history:
</p>

<blockquote style="margin:1em 0; padding:0.5em 1em; background:#f4f4f4; border-left:4px solid #ccc;">
  “That’s one small step for man, one giant leap for mankind.”
</blockquote>

<p>
  Today, our ambitions stretch far beyond Earth’s orbit.
  The <strong>International Space Station</strong> serves as both laboratory and proving ground for extended stays in microgravity.
  Private companies like <strong>SpaceX</strong> and <strong>Blue Origin</strong> have <em>redefined what is possible</em>,
  opening new avenues for exploration and commerce in space.
</p>

<p style="margin-top:1em;">
  Plans are underway to establish a sustained human presence on the Moon and, eventually, Mars—a dream that was once the realm of science fiction.
</p>

<p>
  Yet space is more than a destination.
  It is a <em>canvas of infinite possibility</em>.
  Observatories like the <strong>James Webb Space Telescope</strong> peer deep into the origins of the universe,
  revealing ancient galaxies and potentially habitable exoplanets.
</p>

<p style="margin-top:1em;">
  Every discovery pushes the boundaries of our knowledge, inspiring generations to <strong>look up and wonder.</strong>
</p>

<p>
  As we stand on the threshold of a new era of exploration, one thing is clear:
  <em>our desire to reach beyond the stars will continue to define us.</em>
</p>

<p>
  Whether we travel for science, survival, or sheer curiosity, <strong>the cosmos calls to us, and we will answer.</strong>
</p>

"""
,
            img_url="https://parispeaceforum.org/app/uploads/2023/09/net-zero-space-initiative-1.jpg",
            author=admin_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        existing_post = new_post




@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=register_form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        password = login_form.password.data
        user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=login_form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    initialize_data()
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)



@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, form=comment_form, current_user=current_user)



@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        data = request.form
        name = data['name']
        email = data['email']
        phone = data['phone']
        message = data['message']
        mail_message = f"Subject:Bamboo Blogs: New Message from {name}\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
        if not current_user.is_authenticated:
            flash("You need to login or register to send a message.")
            return redirect(url_for("login"))

        # Send mail
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(email_id, password)
            connection.sendmail(from_addr=email_id, to_addrs="elayabarathiedison@gmail.com", msg=mail_message)

        return render_template('contact.html', tit="Successfully sent your message")
    return render_template('contact.html', tit="Let’s Connect!")


if __name__ == "__main__":
    app.run(debug=True)
