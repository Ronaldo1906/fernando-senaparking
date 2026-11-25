# SenaParking (Flask + Docker)

## Instalar dependencias y ejecutar pruebas localmente
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v

## Arrancar localmente
python app.py

## Construir y ejecutar con Docker
docker build -t senaparking3407180 .
docker run -d -p 5000:5000 --name senaparking3407180_app senaparking3407180