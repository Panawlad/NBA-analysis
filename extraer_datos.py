import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Archivos de entrada/salida
input_file = "boxscores_descargados.txt"
output_file = "team_totals_completo.csv"
log_file = "urls_guardadas.txt"

# Cargar URLs desde archivo
with open(input_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# Cargar URLs ya procesadas (guardadas)
procesadas = set()
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        procesadas = set(line.strip() for line in f)

# Headers para evitar bloqueo
headers = {"User-Agent": "Mozilla/5.0"}

# Comenzar scraping
for i, url in enumerate(urls):
    if url in procesadas:
        continue

    print(f"🔄 [{i+1}/{len(urls)}] Procesando: {url}")
    try:
        r = requests.get(url, headers=headers)

        # Manejo de error 429 (demasiadas peticiones)
        if r.status_code == 429:
            print(f"🚫 429 Too Many Requests en {url}. Esperando 1 hora...")
            time.sleep(3600)
            continue

        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

        registros = []
        for table in soup.find_all("table"):
            table_id = table.get("id", "")
            if table_id.endswith("-game-basic"):
                team = table_id.split("-")[1].upper()
                for row in table.find_all("tr"):
                    if row.find("th") and "Team Totals" in row.find("th").text:
                        stats = [td.text for td in row.find_all("td")]
                        headers_row = [td.get("data-stat") for td in row.find_all("td")]
                        row_data = dict(zip(headers_row, stats))
                        row_data["equipo"] = team
                        row_data["fecha"] = url.split("/")[-1].split(".")[0][:8]
                        row_data["url"] = url
                        registros.append(row_data)

        # Guardar si hubo datos válidos
        if registros:
            df = pd.DataFrame(registros)
            write_mode = "a" if os.path.exists(output_file) else "w"
            header = not os.path.exists(output_file)
            df.to_csv(output_file, mode=write_mode, index=False, header=header)
            with open(log_file, "a") as f:
                f.write(url + "\n")
            print(f"✅ Guardado: {len(registros)} equipos")
        else:
            print(f"⚠️ No se encontró Team Totals en: {url}")

        time.sleep(5)  # Espacio entre solicitudes para evitar bloqueo

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        continue

print("\n✅ Proceso completo. Archivo generado:", output_file)
