from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ServicioParqueo(db.Model):
    __tablename__ = "servicios_parqueo"

    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(120), nullable=False)
    tipo_vehiculo = db.Column(db.String(20), nullable=False)  # automovil, taxi, moto, bicicleta
    placa = db.Column(db.String(20), nullable=False)
    fecha_ingreso = db.Column(db.DateTime, nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=False)
    modalidad = db.Column(db.String(40), nullable=False)
    horas_facturadas = db.Column(db.Float, nullable=False)
    descuento_pct = db.Column(db.Float, nullable=False, default=0.0)
    valor_neto = db.Column(db.Integer, nullable=False)
    impuesto_consumo = db.Column(db.Integer, nullable=False)
    iva = db.Column(db.Integer, nullable=False)
    total_cobrado = db.Column(db.Integer, nullable=False)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente,
            "tipo_vehiculo": self.tipo_vehiculo,
            "placa": self.placa,
            "fecha_ingreso": self.fecha_ingreso.strftime("%d/%m/%Y %H:%M"),
            "fecha_salida": self.fecha_salida.strftime("%d/%m/%Y %H:%M"),
            "modalidad": self.modalidad,
            "horas_facturadas": self.horas_facturadas,
            "descuento_pct": self.descuento_pct,
            "valor_neto": self.valor_neto,
            "impuesto_consumo": self.impuesto_consumo,
            "iva": self.iva,
            "total_cobrado": self.total_cobrado,
        }