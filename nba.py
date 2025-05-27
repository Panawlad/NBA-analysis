import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import time

# Configuración del rango de fechas (desde abril 2024 hasta hoy)
inicio_temporada = datetime(2024, 4, 1)
hoy = datetime.today()

# Ruta del archivo que guarda las URLs ya extraídas
registro_path = "boxscores_descargados.txt"

# Cargar URLs previas si existen
if os.path.exists(registro_path):
    with open(registro_path, "r") as f:
        urls_guardadas = set(line.strip() for line in f)
else:
    urls_guardadas = set()

# Headers para simular navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36"
}

# Comenzar el scraping
fecha = inicio_temporada
urls_nuevas = []

while fecha <= hoy:
    try:
        url = f"https://www.basketball-reference.com/boxscores/?month={fecha.month}&day={fecha.day}&year={fecha.year}"
        response = requests.get(url, headers=headers)

        # Verificar si fue bloqueado
        if response.status_code == 429:
            print("⚠️ Rate limited. Esperando 1 hora...")
            time.sleep(3600)  # Esperar 1 hora
            continue

        if response.status_code != 200:
            print(f"❌ Error {response.status_code} al acceder a {fecha.strftime('%Y-%m-%d')}")
            fecha += timedelta(days=1)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        box_scores = soup.find_all('div', class_='game_summary expanded nohover')

        encontrados = 0
        for box in box_scores:
            enlace = box.find('a', text='Box Score')
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
    time.sleep(5)  # Delay para evitar bloqueo

# Guardar nuevas URLs
with open(registro_path, "a") as f:
    for url in urls_nuevas:
        f.write(url + "\n")

print(f"\n✅ Nuevas URLs guardadas: {len(urls_nuevas)}")
