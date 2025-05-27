from datetime import datetime, timedelta
import subprocess

def main():
    # Ejecutar el script que busca partidos nuevos
    print("🔍 Buscando partidos nuevos...")
    subprocess.run(["python", "nba.py"])

    # Ejecutar el script que procesa las URLs descargadas
    print("📊 Procesando box scores...")
    subprocess.run(["python", "prueba.py"])

if __name__ == "__main__":
    main()
