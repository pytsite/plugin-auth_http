"""PytSite Auth UI Plugin Events Handlers
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from datetime import datetime as _datetime
from pytsite import router as _router
from plugins import auth as _auth


def on_router_dispatch():
    """pytsite.router.dispatch Event Handler
    """
    # User is anonymous by default
    user = _auth.get_anonymous_user()

    # Switch current user
    session = _router.session()
    if 'auth.login' in session:
        try:
            user = _auth.get_user(session['auth.login'])
        except _auth.error.UserNotFound:
            # User has been deleted, so delete session information about it
            del session['auth.login']
            session.modified = True

    # Set current user
    _auth.switch_user(user)

    if not user.is_anonymous:
        if user.status == _auth.USER_STATUS_ACTIVE:
            # Disable page caching for signed in users
            _router.no_cache(True)

            # Update user's activity timestamp
            user.last_activity = _datetime.now()
            user.save()

            # Update session's timestamp
            session.modified = True
        else:
            # Sign out inactive user
            _auth.sign_out(user)


def on_auth_sign_in(user: _auth.AbstractUser):
    # Set session marker
    s = _router.session()
    s['auth.login'] = user.login
    s.modified = True

    # Update IP address and geo data
    user.last_ip = _router.request().remote_addr
    geo_ip = user.geo_ip
    if not user.timezone:
        user.timezone = geo_ip.timezone
    if not user.country:
        user.country = geo_ip.country
    if not user.city:
        user.city = geo_ip.city

    user.save()


def on_auth_sign_out(user: _auth.AbstractUser):
    s = _router.session()
    del s['auth.login']
    s.modified = True
