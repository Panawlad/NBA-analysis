from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup
import time

# Ruta del archivo que guarda las URLs ya extraídas
registro_path = "boxscores_descargados.txt"

# Leer fechas anteriores desde las URLs guardadas
if os.path.exists(registro_path):
    with open(registro_path, "r") as f:
        urls_guardadas = set(line.strip() for line in f if line.strip())

    # Obtener la última fecha registrada en el archivo
    fechas_guardadas = [line.split("/")[-1].split(".")[0][:8] for line in urls_guardadas]
    fechas_guardadas.sort()
    ultima_fecha = datetime.strptime(fechas_guardadas[-1], "%Y%m%d")
    inicio_busqueda = ultima_fecha + timedelta(days=1)  # Continuar desde el día siguiente
else:
    urls_guardadas = set()
    inicio_busqueda = datetime(2024, 4, 1)  # Primera fecha por defecto si no existe el archivo

hoy = datetime.today()
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Comenzar el scraping desde la última fecha
fecha = inicio_busqueda
urls_nuevas = []

while fecha <= hoy:
    try:
        url = f"https://www.basketball-reference.com/boxscores/?month={fecha.month}&day={fecha.day}&year={fecha.year}"
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            print("⚠️ Rate limited. Esperando 1 hora...")
            time.sleep(3600)
            continue

        if response.status_code != 200:
            print(f"❌ Error {response.status_code} al acceder a {fecha.strftime('%Y-%m-%d')}")
            fecha += timedelta(days=1)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        box_scores = soup.find_all('div', class_='game_summary expanded nohover')

        encontrados = 0
        for box in box_scores:
            enlace = box.find('a', string='Box Score')  # Cambiado 'text' → 'string' (para evitar warning)
            if enlace:
                url_completa = "https://www.basketball-reference.com" + enlace['href']
                if url_completa not in urls_guardadas:
                    urls_nuevas.append(url_completa)
                    urls_guardadas.add(url_completa)
                    encontrados += 1

        print(f"📅 {fecha.strftime('%Y-%m-%d')} - {encontrados} partido(s) nuevo(s) encontrado(s).")

    except Exception as e:
        print(f"⚠️ Error en {fecha.strftime('%Y-%m-%d')}: {e}")

    fecha += timedelta(days=1)
    time.sleep(5)

# Guardar nuevas URLs encontradas
if urls_nuevas:
    with open(registro_path, "a") as f:
        for url in urls_nuevas:
            f.write(url + "\n")

print(f"\n✅ Nuevas URLs guardadas: {len(urls_nuevas)}")
