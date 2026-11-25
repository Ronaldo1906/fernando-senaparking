import os
import tempfile
import unittest
from datetime import datetime
from app import create_app
from billing import calcular_liquidacion
from models import db


class TestSenaParkingBilling(unittest.TestCase):
    def test_tarifa_auto_por_hora(self):
        res = calcular_liquidacion(
            "Carlos",
            "automovil",
            "ABC123",
            datetime(2026, 11, 20, 8, 0),
            datetime(2026, 11, 20, 11, 0),
        )
        self.assertEqual(res["total_cobrado"], 6300)

    def test_descuento_taxi_adicional(self):
        res = calcular_liquidacion(
            "Pedro",
            "taxi",
            "TXI999",
            datetime(2026, 11, 20, 8, 0),
            datetime(2026, 11, 20, 11, 0),
        )
        self.assertEqual(res["descuento_pct"], 2.0)
        self.assertEqual(res["total_cobrado"], 6174)

    def test_amanecer_moto_con_descuento_nocturno(self):
        res = calcular_liquidacion(
            "Simón",
            "moto",
            "FSB79",
            datetime(2026, 10, 19, 21, 42),
            datetime(2026, 10, 19, 22, 43),
            modalidad_solicitada="amanecer",
        )
        self.assertEqual(res["descuento_pct"], 8.0)
        self.assertEqual(res["total_cobrado"], 10120)

    def test_bicicleta_no_aplica_amanecer(self):
        with self.assertRaises(ValueError):
            calcular_liquidacion(
                "Ana",
                "bicicleta",
                "BIC01",
                datetime(2026, 11, 20, 20, 0),
                datetime(2026, 11, 21, 5, 0),
                modalidad_solicitada="amanecer",
            )


class TestSenaParkingWeb(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.db_path}",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_registrar_y_consultar_servicio(self):
        resp = self.client.post(
            "/",
            data={
                "cliente": "Simón Tolomeo",
                "placa": "FSB79",
                "tipo_vehiculo": "moto",
                "modalidad": "por_hora",
                "fecha_ingreso": "2026-10-19T21:42",
                "fecha_salida": "2026-10-19T22:43",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"FSB79", resp.data)

        listado = self.client.get("/servicios?q=FSB79")
        self.assertEqual(listado.status_code, 200)
        self.assertIn(b"Sim", listado.data)


if __name__ == "__main__":
    unittest.main()