from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import psycopg2.extras

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('accounts', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    error = None
    cur.execute('SELECT * FROM account')
    
    accounts = cur.fetchall()
    return accounts

@bp.route('/<id>', methods=('GET', 'POST'))
@login_required
def get_or_update(id):
    return {'error': 'not found'}