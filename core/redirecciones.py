# core/redirecciones.py
"""
Redirecciones dinámicas por return_to.
"""

import logging
from urllib.parse import urlparse, urlunparse

from flask import current_app, redirect, request, url_for
from werkzeug.routing import BuildError

logger = logging.getLogger(__name__)


def normalizar_texto(valor):
    if valor is None:
        return ''
    return str(valor).strip()


def endpoint_existe(endpoint):
    endpoint = normalizar_texto(endpoint)

    if not endpoint:
        return False

    try:
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint == endpoint:
                return True
    except Exception:
        return False

    return False


def endpoint_desde_referrer(endpoint_mapping=None):
    referrer = request.referrer or ''

    if not referrer:
        return ''

    try:
        path = urlparse(referrer).path or ''
    except Exception:
        return ''

    mapping = endpoint_mapping or {
        '/graficos_repuestos': 'indexgraficos_repuestos.indexgraficos_repuestos',
        '/lista_repuestos': 'indexlista_repuestos.indexlista_repuestos',
        '/inventario': 'indexinventario.indexinventario',
        '/estadosRep': 'indexEstadoRep.indexEstadoRep',
    }

    for prefijo, endpoint in mapping.items():
        if path.startswith(prefijo):
            return endpoint

    return ''


def url_interna_desde_referrer(endpoint):
    referrer = request.referrer or ''

    if not referrer:
        return None

    try:
        parsed = urlparse(referrer)

        if parsed.scheme and parsed.scheme not in ('http', 'https'):
            return None

        if parsed.netloc and parsed.netloc != request.host:
            return None

        try:
            expected_path = urlparse(url_for(endpoint)).path
        except Exception:
            return None

        if parsed.path != expected_path:
            return None

        return urlunparse(parsed)
    except Exception:
        return None


def redirigir_return_to(
    return_to,
    tab_activo='',
    default_endpoint='indexEstadoRep.indexEstadoRep',
    endpoint_mapping=None
):
    endpoint = normalizar_texto(return_to)

    if not endpoint or not endpoint_existe(endpoint):
        endpoint_from_referrer = endpoint_desde_referrer(endpoint_mapping)

        if endpoint_from_referrer and endpoint_existe(endpoint_from_referrer):
            endpoint = endpoint_from_referrer
        else:
            endpoint = default_endpoint

    referrer_url = url_interna_desde_referrer(endpoint)

    if referrer_url:
        return redirect(referrer_url)

    kwargs = {}

    if endpoint == 'indexEstadoRep.indexEstadoRep' and tab_activo:
        kwargs['active_tab'] = tab_activo

    try:
        return redirect(url_for(endpoint, **kwargs))
    except BuildError:
        logger.warning(
            f"redirigir_return_to: endpoint inválido '{endpoint}'. "
            f"Fallback a '{default_endpoint}'"
        )

        try:
            if default_endpoint == 'indexEstadoRep.indexEstadoRep' and tab_activo:
                return redirect(url_for(default_endpoint, active_tab=tab_activo))

            return redirect(url_for(default_endpoint))
        except Exception:
            return redirect('/')