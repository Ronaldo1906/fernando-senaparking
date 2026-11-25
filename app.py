import os
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from billing import ETIQUETAS_VEHICULO, calcular_liquidacion, parsear_fecha_hora
from models import ServicioParqueo, db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    default_db_path = os.path.join(app.instance_path, "senaparking.db")
    app.config.from_mapping(
        SECRET_KEY="senaparking-dev-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{default_db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def index():
        error = None
        if request.method == "POST":
            try:
                fecha_ingreso = parsear_fecha_hora(request.form.get("fecha_ingreso", ""))
                fecha_salida = parsear_fecha_hora(request.form.get("fecha_salida", ""))
                calculo = calcular_liquidacion(
                    cliente=request.form.get("cliente", ""),
                    tipo_vehiculo=request.form.get("tipo_vehiculo", ""),
                    placa=request.form.get("placa", ""),
                    fecha_ingreso=fecha_ingreso,
                    fecha_salida=fecha_salida,
                    modalidad_solicitada=request.form.get("modalidad", "auto"),
                )
                servicio = ServicioParqueo(**calculo)
                db.session.add(servicio)
                db.session.commit()
                return redirect(url_for("ver_factura", servicio_id=servicio.id))
            except ValueError as exc:
                error = str(exc)

        recientes = ServicioParqueo.query.order_by(ServicioParqueo.id.desc()).limit(10).all()
        return render_template(
            "index.html",
            error=error,
            recientes=recientes,
            etiquetas=ETIQUETAS_VEHICULO,
        )

    @app.route("/factura/<int:servicio_id>")
    def ver_factura(servicio_id):
        servicio = db.session.get(ServicioParqueo, servicio_id)
        if not servicio:
            abort(404)
        return render_template(
            "factura.html",
            servicio=servicio,
            etiqueta_vehiculo=ETIQUETAS_VEHICULO.get(servicio.tipo_vehiculo, servicio.tipo_vehiculo),
        )

    @app.route("/servicios")
    def listar_servicios():
        q = (request.args.get("q") or "").strip()
        query = ServicioParqueo.query
        if q:
            patron = f"%{q}%"
            query = query.filter(
                (ServicioParqueo.cliente.ilike(patron)) | (ServicioParqueo.placa.ilike(patron))
            )
        servicios = query.order_by(ServicioParqueo.id.desc()).all()
        return render_template(
            "servicios.html",
            servicios=servicios,
            q=q,
            etiquetas=ETIQUETAS_VEHICULO,
        )

    @app.route("/api/servicios/<int:servicio_id>")
    def api_servicio(servicio_id):
        servicio = db.session.get(ServicioParqueo, servicio_id)
        if not servicio:
            abort(404)
        return jsonify(servicio.to_dict())

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)