# core/crud_bp.py
"""
Blueprint genérico para CRUD de listas planas (no jerárquicas).
Reutilizable para: tareas, eventos de agenda, pagos, etc.

Uso:
    from core.crud_bp import crear_blueprint_crud

    bp = crear_blueprint_crud(
        nombre_bp='tareas',
        data_file='data/tareas/tareas.json',
        template='apps/tareas/templates/tareas.html',
        vista_url='/tareas',
        api_url='/api/tareas',
        campos_requeridos=['titulo', 'fecha'],
        campos_default={'descripcion': ''},
        nombre_item='tarea'
    )
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from core.db_json import JsonStore
from core.menu import cargar_menu


def crear_blueprint_crud(
    nombre_bp,
    data_file,
    template,
    vista_url,
    api_url,
    campos_requeridos=None,
    campos_default=None,
    nombre_item="item",
    endpoint_vista=None,
    extra_context=None,
):
    """
    Factory que crea un Blueprint con CRUD completo.

    Args:
        nombre_bp: Nombre del blueprint
        data_file: Ruta al archivo JSON
        template: Template HTML a renderizar
        vista_url: URL de la vista principal
        api_url: URL base para la API REST
        campos_requeridos: Lista de campos obligatorios
        campos_default: Dict con valores por defecto
        nombre_item: Nombre del item (para mensajes)
        endpoint_vista: Nombre del endpoint de la vista
        extra_context: Función que retorna contexto adicional

    Returns:
        Blueprint configurado con rutas GET/POST/PUT/DELETE
    """
    campos_requeridos = campos_requeridos or []
    campos_default = campos_default or {}
    endpoint_vista = endpoint_vista or f"index_{nombre_bp}"

    bp = Blueprint(nombre_bp, __name__, template_folder="templates")
    store = JsonStore(data_file)

    # ------------------------------------------------------------------
    # Vista principal
    # ------------------------------------------------------------------
    @bp.route(vista_url, endpoint=endpoint_vista)
    @login_required
    def vista_principal():
        items = store.cargar()
        context = {
            "nemu": cargar_menu(),
            "roles": current_user.roles,
            "items": items,
            "nombre_item": nombre_item,
            "campos_requeridos": campos_requeridos,
        }
        if extra_context:
            context.update(extra_context())
        return render_template(template, **context)

    # ------------------------------------------------------------------
    # API: Listar todos
    # ------------------------------------------------------------------
    @bp.route(api_url, methods=["GET"], endpoint="api_listar")
    @login_required
    def api_listar():
        return jsonify(store.cargar())

    # ------------------------------------------------------------------
    # API: Obtener uno
    # ------------------------------------------------------------------
    @bp.route(f"{api_url}/<int:item_id>", methods=["GET"], endpoint="api_obtener")
    @login_required
    def api_obtener(item_id):
        item = store.buscar_uno(id=item_id)
        if not item:
            return jsonify({"msg": f"{nombre_item.capitalize()} no encontrado"}), 404
        return jsonify(item)

    # ------------------------------------------------------------------
    # API: Crear
    # ------------------------------------------------------------------
    @bp.route(api_url, methods=["POST"], endpoint="api_crear")
    @login_required
    def api_crear():
        data = request.get_json() or {}

        # Validar campos requeridos
        faltantes = [c for c in campos_requeridos if not data.get(c)]
        if faltantes:
            return jsonify({
                "msg": f"Faltan campos obligatorios: {', '.join(faltantes)}",
                "type": "error"
            }), 400

        # Aplicar valores por defecto
        for clave, valor in campos_default.items():
            data.setdefault(clave, valor)

        item = store.agregar(data)
        return jsonify({
            "msg": f"{nombre_item.capitalize()} creado correctamente",
            "type": "success",
            "item": item
        }), 201

    # ------------------------------------------------------------------
    # API: Actualizar
    # ------------------------------------------------------------------
    @bp.route(f"{api_url}/<int:item_id>", methods=["PUT"], endpoint="api_editar")
    @login_required
    def api_editar(item_id):
        if not store.existe(item_id):
            return jsonify({"msg": f"{nombre_item.capitalize()} no encontrado"}), 404

        data = request.get_json() or {}

        # Validar campos requeridos (solo los enviados)
        faltantes = [c for c in campos_requeridos if c in data and not data.get(c)]
        if faltantes:
            return jsonify({
                "msg": f"Campos inválidos: {', '.join(faltantes)}",
                "type": "error"
            }), 400

        store.editar(item_id, data)
        return jsonify({
            "msg": f"{nombre_item.capitalize()} actualizado correctamente",
            "type": "success"
        })

    # ------------------------------------------------------------------
    # API: Eliminar
    # ------------------------------------------------------------------
    @bp.route(f"{api_url}/<int:item_id>", methods=["DELETE"], endpoint="api_eliminar")
    @login_required
    def api_eliminar(item_id):
        if not store.existe(item_id):
            return jsonify({"msg": f"{nombre_item.capitalize()} no encontrado"}), 404

        store.eliminar(item_id)
        return jsonify({
            "msg": f"{nombre_item.capitalize()} eliminado correctamente",
            "type": "success"
        })

    # ------------------------------------------------------------------
    # API: Toggle booleano (útil para "realizado", "pagado", etc.)
    # ------------------------------------------------------------------
    @bp.route(
        f"{api_url}/<int:item_id>/toggle/<campo>",
        methods=["PATCH"],
        endpoint="api_toggle"
    )
    @login_required
    def api_toggle(item_id, campo):
        item = store.buscar_uno(id=item_id)
        if not item:
            return jsonify({"msg": "Item no encontrado"}), 404

        nuevo_valor = not item.get(campo, False)
        store.editar(item_id, {campo: nuevo_valor})
        return jsonify({
            "msg": "Estado actualizado",
            "type": "success",
            "valor": nuevo_valor
        })

    return bp