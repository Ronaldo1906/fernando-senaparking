import math
from datetime import datetime

TARIFAS_HORA = {
    "automovil": 2100,
    "taxi": 2100,
    "moto": 1200,
    "bicicleta": 450,
}

TARIFAS_AMANECER = {
    "automovil": 15000,
    "taxi": 15000,
    "moto": 11000,
}

TARIFAS_24H = {
    "automovil": 20000,
    "taxi": 20000,
    "moto": 15000,
}

TARIFAS_SEMANAL = {
    "automovil": 126000,
    "taxi": 126000,
    "moto": 94500,
}

ETIQUETAS_VEHICULO = {
    "automovil": "Automóvil",
    "taxi": "Taxi",
    "moto": "Motocicleta",
    "bicicleta": "Bicicleta",
}


def parsear_fecha_hora(valor: str) -> datetime:
    if not valor or not valor.strip():
        raise ValueError("La fecha y hora es obligatoria.")
    texto = valor.strip()
    formatos = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %I:%M %p",
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue
    raise ValueError("Formato de fecha y hora inválido.")


def es_horario_amanecer(ingreso: datetime, salida: datetime) -> bool:
    """Verifica si la estadía se ubica en el horario nocturno (6 p. m. a 6 a. m.)."""
    horas_totales = (salida - ingreso).total_seconds() / 3600.0
    if horas_totales <= 0 or horas_totales > 14:
        return False

    def en_ventana_nocturna(dt: datetime) -> bool:
        return dt.hour >= 18 or dt.hour < 6

    return en_ventana_nocturna(ingreso) and en_ventana_nocturna(salida)


def calcular_liquidacion(
    cliente: str,
    tipo_vehiculo: str,
    placa: str,
    fecha_ingreso: datetime,
    fecha_salida: datetime,
    modalidad_solicitada: str = "auto",
) -> dict:
    cliente_limpio = (cliente or "").strip()
    placa_limpia = (placa or "").strip().upper()
    tipo = (tipo_vehiculo or "").strip().lower()
    modalidad_req = (modalidad_solicitada or "auto").strip().lower()

    if not cliente_limpio:
        raise ValueError("El nombre del cliente es obligatorio.")
    if not placa_limpia:
        raise ValueError("La placa o identificación es obligatoria.")
    if tipo not in TARIFAS_HORA:
        raise ValueError("Tipo de vehículo no válido.")
    if fecha_salida <= fecha_ingreso:
        raise ValueError("La hora de salida debe ser posterior a la hora de ingreso.")

    duracion_horas = (fecha_salida - fecha_ingreso).total_seconds() / 3600.0
    horas_cobro = max(1, math.ceil(duracion_horas))

    if tipo == "bicicleta" and modalidad_req in {"amanecer", "24h", "semanal"}:
        raise ValueError("La modalidad seleccionada no aplica para bicicletas.")
    if tipo == "bicicleta" and duracion_horas > 24:
        raise ValueError("Las bicicletas no aplican para estadías de 24 horas o más.")

    descuento_pct = 0.0
    if tipo == "taxi":
        descuento_pct += 2.0

    if modalidad_req == "semanal" or duracion_horas > 168:
        if tipo == "bicicleta":
            raise ValueError("La tarifa semanal no aplica para bicicletas.")
        semanas = max(1, math.ceil(duracion_horas / 168.0))
        base = TARIFAS_SEMANAL[tipo] * semanas
        modalidad_final = "Semanal"
    elif modalidad_req == "24h" or (24.0 <= duracion_horas <= 168.0 and modalidad_req == "auto"):
        if tipo == "bicicleta":
            raise ValueError("La estadía de 24 horas no aplica para bicicletas.")
        if duracion_horas < 24.0:
            base = TARIFAS_HORA[tipo] * horas_cobro
            descuento_pct += 6.0
        else:
            dias_24h = max(1, math.ceil(duracion_horas / 24.0))
            base = TARIFAS_24H[tipo] * dias_24h
        modalidad_final = "24 horas"
    elif modalidad_req == "amanecer" or (modalidad_req == "auto" and es_horario_amanecer(fecha_ingreso, fecha_salida)):
        if tipo == "bicicleta":
            raise ValueError("El parqueo de amanecer no aplica para bicicletas.")
        if es_horario_amanecer(fecha_ingreso, fecha_salida):
            base = TARIFAS_AMANECER[tipo]
            descuento_pct += 8.0
        else:
            base = TARIFAS_HORA[tipo] * horas_cobro
        modalidad_final = "Amanecer"
    else:
        base = TARIFAS_HORA[tipo] * horas_cobro
        if duracion_horas >= 10.0:
            descuento_pct += 6.0
        elif duracion_horas >= 6.0:
            descuento_pct += 5.0
        modalidad_final = "Por hora"

    total_cobrado = int(round(base * (1.0 - descuento_pct / 100.0)))

    impuesto_consumo = int(round(total_cobrado * 0.01))
    iva = int(round(total_cobrado * 0.19))
    valor_neto = total_cobrado - impuesto_consumo - iva

    return {
        "cliente": cliente_limpio,
        "tipo_vehiculo": tipo,
        "placa": placa_limpia,
        "fecha_ingreso": fecha_ingreso,
        "fecha_salida": fecha_salida,
        "modalidad": modalidad_final,
        "horas_facturadas": round(duracion_horas, 2),
        "descuento_pct": round(descuento_pct, 2),
        "valor_neto": valor_neto,
        "impuesto_consumo": impuesto_consumo,
        "iva": iva,
        "total_cobrado": total_cobrado,
    }