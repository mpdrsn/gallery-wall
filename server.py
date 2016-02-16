
from flask import (Flask, render_template, jsonify,
                   request, redirect, flash, session)

from jinja2 import StrictUndefined

from model import User, Picture, Gallery, Wall, Placement
from model import connect_to_db, db

from arrange import arrange_gallery_1

# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "^*V6Er$&!DN9dzMrpP994*Mx2"

# Jinja should not fail silently
app.jinja_env.undefined = StrictUndefined

DEFAULT_USER_ID = 1


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/navigation')
def navigation():
    """Navigate to various functional pages after login/guest.

    May be encorperated as navbar later.
    """

    return render_template("navigation.html")


@app.route('/login')
def prompt_login():
    """Page displaying forms to log in or sign up as user."""

    return render_template("login.html")


@app.route('/login-process', methods=['POST'])
def process_login():
    """Handle form submission for login process."""

    attempted_username = request.form.get('username').strip().lower()
    attempted_password = request.form.get('password')

    user = User.query.filter(User.username == attempted_username).first()

    if (user is None) or not attempted_username:
        flash("Nonexistent user. Please retry log in.")
        return redirect('/login')

    elif attempted_password == user.password:
        session['user_id'] = user.user_id
        session['username'] = user.username

        flash("Successful log in! Welcome {}.".format(user.username))
        return redirect('/navigation')

    else:
        flash("Invalid password.")
        return redirect('/login')


@app.route('/signup-process', methods=['POST'])
def process_signup():
    """Handle form submission for signup process."""

    attempted_username = request.form.get('username').strip().lower()
    attempted_email = request.form.get('email')
    attempted_password = request.form.get('password')

    user = User.query.filter(User.username == attempted_username).first()

    if (user is None) and attempted_username:
        # User not already existing, and a username was entered
        user = User(username=attempted_username,
                    email=attempted_email,
                    password=attempted_password)
        db.session.add(user)
        db.session.commit()

        flash("Sign up successful! Now log in.")
        return redirect('/login')

    else:
        flash("Invalid sign up attempt.")
        return redirect('/login')


@app.route('/logout-process')
def process_logout():
    """Handle form submission for logout process."""

    session.pop('user_id', None)

    # flash message: logout successs
    flash("Successful log out. Goodbye!")
    return redirect('/')


@app.route('/galleries')
def show_galleries():
    """Show a user's galleries that they can choose to arrange."""

    user_id = session.get('user_id', DEFAULT_USER_ID)

    galleries = User.query.get(user_id).galleries
    gallery_ids = [g.gallery_id for g in galleries]

    return render_template("galleries.html",
                           gallery_ids=gallery_ids)


@app.route('/arrange', methods=["GET"])
def prompt_arrangment():
    """Allow a user to input parameters about wall generation from gallery."""

    gallery_id = request.args.get('gallery_id')
    curator_id = Gallery.query.get(gallery_id).curator_id

    # This is a get request because it does not have side effects, but check
    # they are the curator of this gallery or that it is site sample.
    if curator_id not in [session.get('user_id'), DEFAULT_USER_ID]:
        gallery_id = None

    return render_template("arrange.html",
                           gallery_id=gallery_id)


@app.route('/arrange-o-matic', methods=["POST"])
def process_arrangment():
    """Process the arrangement."""

    gallery_id = request.form.get('gallery_id')

    print "I'M THE ARRANGE-O-MATIC!!!!!"
    placements, width, height = arrange_gallery_1(gallery_id, {})

    wall = Wall(gallery_id=gallery_id,
                wall_width=width,
                wall_height=height,
                )
    db.session.add(wall)
    db.session.commit()
    wall_id = wall.wall_id

    for picture_id in placements:
        placement = Placement(wall_id=wall_id,
                              picture_id=picture_id,
                              x_coord=placements[picture_id]['x'],
                              y_coord=placements[picture_id]['y'])

        db.session.add(placement)
    db.session.commit()

    # TODO: change to redirect
    return render_template("new-wall.html",
                           wall_id=wall_id,
                           )


@app.route('/walls')
def show_walls():
    """Show a user's walls that they have arranged and saved."""

    user_id = session.get('user_id', DEFAULT_USER_ID)

    walls = User.query.get(user_id).walls
    wall_ids = [w.wall_id for w in walls]

    return render_template("walls.html",
                           wall_ids=wall_ids,
                           )


@app.route('/new-wall')
def show_new_wall():
    """Show a user wall that has just been arranged."""

    wall_id = 1

    return render_template("new-wall.html",
                           wall_id=wall_id,
                           )


@app.route('/getwall.json')
def get_wall_data():
    """Get the information needed for displaying a wall.

    Response to an AJAX request.
    """

    wall_id = request.args.get('wallid')
    wall = Wall.query.get(wall_id)

    if wall:
        wall_to_hang = wall.get_hanging_info()
    else:
        wall_to_hang = {'id': None}

    return jsonify(wall_to_hang)


@app.route('/getgallery.json')
def get_gallery_data():
    """Get the information needed for displaying a gallery.

    Response to an AJAX request.
    """

    gallery_id = request.args.get('galleryid')
    gallery = Gallery.query.get(gallery_id)

    print('getting gallery:')
    print(gallery)

    if gallery:
        gallery_to_hang = gallery.get_display_info()
    else:
        gallery_to_hang = {'id': None}

    return jsonify(gallery_to_hang)


if __name__ == "__main__":
    # Use debug mode
    app.debug = True

    connect_to_db(app)

    # # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()