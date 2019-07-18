"""PytSite Auth UI Plugin Events Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from datetime import datetime
from pytsite import router, reg
from plugins import auth


def on_router_dispatch():
    """pytsite.router.dispatch Event Handler
    """
    # User is anonymous by default
    user = auth.get_anonymous_user()

    # Switch current user
    session = router.session()
    if 'auth.login' in session:
        try:
            user = auth.get_user(session['auth.login'])
        except auth.error.UserNotFound:
            # User has been deleted, so delete session information about it
            del session['auth.login']
            session.modified = True

    # Set current user
    auth.switch_user(user)

    if not user.is_anonymous:
        if user.status == auth.USER_STATUS_ACTIVE:
            # Disable page caching for signed in users
            if router.request().method == 'GET':
                router.no_cache(True)
                router.no_store(True)
                router.private(True)
                router.max_age(0)

            # Update user's activity timestamp
            now = datetime.now()
            la_delta = now - (user.last_activity if user.last_activity else datetime(1970, 1, 1))
            if not router.request().is_xhr and (not user.last_activity or la_delta.days or la_delta.seconds > 60):
                user.set_field('last_activity', now).save()

            # Update session's timestamp
            session.modified = True
        else:
            # Sign out inactive user
            auth.sign_out(user)


def on_auth_sign_in(user: auth.AbstractUser):
    # Set session marker
    s = router.session()
    s['auth.login'] = user.login
    s.modified = True

    # Update IP address and geo data
    user.last_ip = router.request().real_remote_addr

    if reg.get('auth.user_geo_set', True):
        geo_ip = user.geo_ip

        if not user.timezone:
            user.timezone = geo_ip.timezone
        if not user.country:
            user.country = geo_ip.country
        if not user.city:
            user.city = geo_ip.city

    user.save()


def on_auth_sign_out(user: auth.AbstractUser):
    s = router.session()
    del s['auth.login']
    s.modified = True
