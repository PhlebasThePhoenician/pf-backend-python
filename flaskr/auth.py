import functools
import bcrypt
import psycopg2.extras

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                pw_hash = bcrypt.hashpw( bytes(password, 'utf-8'), bcrypt.gensalt())
                cur.execute(
                    "INSERT INTO public.user (email, passwd) VALUES (%s, %s)",
                    (username, pw_hash.decode("utf-8")),
                )
                #cur.execute("insert into user (email, passwd) values('huttu','juttu')")
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        #username = request.form['username']
        #password = request.form['password']
        #json = request.json()
        data = request.get_json()
        db = get_db()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        error = None
        cur.execute(
            'SELECT * FROM public.user WHERE email = %s', (data['username'],)
        )
        user = cur.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not bcrypt.checkpw(bytes(data['password'], 'utf-8'), bytes(user['passwd'], 'utf-8')):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cur = get_db().cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT * FROM public.user WHERE id = %s', (user_id,)
        )
        g.user = cur.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view