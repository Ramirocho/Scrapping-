from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By

# Crear opciones para Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument('--log-level=1')

# Configuración de WebDriver con webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Base URL
base_url = "https://www.pompeyo.cl/categoria-producto/autos/usados/page/{}"

# Listas para almacenar datos de todas las páginas
datos_combinados = []

# Contador de páginas
page_count = 1

# Bucle para recorrer las páginas lo defino asi para que sea en teoria un bucle infinito pero luego ya valido el tema del html para que se termine
while True: 
    print(f"Procesando página {page_count}...")
    # Construir la URL dinámica
    url = base_url.format(page_count)
    driver.get(url)
    
    # Esperar a que la página cargue completamente 
    time.sleep(4)
    
    # Analizar el contenido de la página
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extraer datos de la página actual
    Nombre = [element.get_text(" ", strip=True) for element in soup.find_all(class_='wd-entities-title')]
    Caracteristicas = [element.get_text(strip=True) for element in soup.find_all(class_='product-meta-info')] 
    Precio = [element.get_text(strip=True) for element in soup.find_all(class_='price')]
    
    # Verificar si la página no tiene resultados
    if not Nombre:  # Si no hay nombres, asumimos que no hay más datos
        print("No hay más resultados. Finalizando.")
        break

    # Procesar los datos extraídos
    for i, nombre in enumerate(Nombre):
        # Dividir Nombre en Marca y Modelo esto por contexto del html en la clase encuentro estos dos datos
        partes_nombre = nombre.split()
        if len(partes_nombre) >= 2:
            marca = partes_nombre[0]
            modelo = " ".join(partes_nombre[1:])
        else:
            marca = nombre
            modelo = None

        # Procesar Características aca me figuran siempre 4 asi que asumo esto agregue un validador en caso de que no ocurra esto tirara unos nulos
        if i < len(Caracteristicas):  # Evitar errores si hay más nombres que características
            partes_caracteristicas = Caracteristicas[i].split('|')
            if len(partes_caracteristicas) == 4:
                modelo2, descripcion, anio, tipo = [parte.strip() for parte in partes_caracteristicas]
            else:
                modelo2 = descripcion = anio = tipo = None
        else:
            modelo2 = descripcion = anio = tipo = None

        # Procesar Precio
        precio = Precio[i] if i < len(Precio) else None

        # Combinar todo 
        datos_combinados.append({
            "marca": marca,
            "modelo": modelo,
            "modelo2": modelo2,
            "descripcion": descripcion,
            "anio": anio,
            "tipo": tipo,
            "precio": precio
        })

    # Incrementar el contador de páginas para pasar a la siguiente
    page_count += 1

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo Excel
df = pd.DataFrame(datos_combinados)

try:
    df.to_excel('C:/Users/Pc/Desktop/vehiculos_Pompeyo.xlsx', index=False)
    print("Datos guardados en 'vehiculos_Pompeyo.xlsx'")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")
