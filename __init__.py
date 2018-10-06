"""PytSite Auth HTTP Plugin Events Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load_wsgi():
    from pytsite import router
    from plugins import auth as _auth
    from . import _eh

    # Router events
    router.on_dispatch(_eh.on_router_dispatch, -999, '*')
    router.on_xhr_dispatch(_eh.on_router_dispatch, -999, '*')

    # Auth events
    _auth.on_sign_in(_eh.on_auth_sign_in)
    _auth.on_sign_out(_eh.on_auth_sign_out)
