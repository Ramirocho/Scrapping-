from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Crear opciones para Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument('--log-level=1')

# Configuración de WebDriver con webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Iniciar la sesión de WebDriver
driver.get("https://autotattersall.cl/autos-usados")
driver.maximize_window()
time.sleep(10)  # Espera para la carga inicial de la página

# Listas para almacenar datos de todas las páginas
nombres = []
modelos = []
anios = []
kilometrajes = []
combustible = []
tipos = []
precios = []

# Contador de páginas
page_count = 1

# Bucle para recorrer todas las páginas
while True:
    try:
        # Crear objeto BeautifulSoup para la página actual
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extraer datos
        Nombre = [element.get_text(strip=True) for element in soup.find_all(class_='cardMarca')]
        Modelo = [element.get_text(strip=True) for element in soup.find_all(class_='cardModelo')]

        # Extraer las tres características: año, kilometraje y tipo
        caracteristicas = [element.get_text(strip=True) for element in soup.find_all(class_='detailText')]
        Anio = caracteristicas[0::4]
        Combustible = caracteristicas[1::4]
        Tipo = caracteristicas[2::4]
        Kilometraje = caracteristicas[3::4]

        Precio = [element.get_text(strip=True) for element in soup.find_all(class_='precio')]

        # Agregar los datos al DataFrame
        #for i in range(len(Modelo)):
        for i in range (len(Modelo)) :
            nombres.append(Nombre[i])
            modelos.append(Modelo[i])
            anios.append(Anio[i] if i < len(Anio) else None)
            combustible.append(Combustible[i] if i < len(Combustible) else None)
            kilometrajes.append(Kilometraje[i] if i < len(Kilometraje) else None)
            tipos.append(Tipo[i] if i < len(Tipo) else None)
            precios.append(Precio[i] if i < len(Precio) else None)

        # Intentar ir a la siguiente página
        try:
            # Localizar y hacer clic en el botón "Siguiente"
            #next_button = driver.find_element(By.LINK_TEXT, "›")  # Usar el texto que aparece en el botón
            #next_button= driver.find_element(By.CLASS_NAME, "p-icon p-paginator-next-icon")
            #ActionChains(driver).move_to_element(next_button).click().perform()  # Hacer clic en el botón "Siguiente"
            # Encuentra el botón de "Siguiente"
            next_button = driver.find_element(By.CLASS_NAME, "p-icon.p-paginator-next-icon")
            next_button.click()
            time.sleep(5)  # Esperar para cargar la siguiente página
            
            # Incrementar el contador y mostrar el progreso en consola
            page_count += 1
            print(f"Página {page_count} recorrida con éxito.")
        
        except Exception as e:
            print("No se pudo acceder al botón 'Siguiente'. Saltando a la siguiente página.")
            print(f"Error: {e}")  # Imprimir el error si lo hay
            break  # Termina el bucle si hay un problema con el botón 'Siguiente'

    except Exception as e:
        print("Ocurrió un error al procesar la página.")
        print(f"Error: {e}")  # Imprimir el error si lo hay
        # Cerrar el navegador y salir del bucle en caso de error
        break

# Cerrar el navegador
driver.quit()

# Crear un DataFrame de pandas con los datos recopilados de todas las páginas
data = {
    'Nombre': nombres,
    'Modelo': modelos,
    'Año': anios,
    'Kilometraje': kilometrajes,
    'Tipo': tipos,
    'Combustible': combustible,
    'Precio': precios
}
df = pd.DataFrame(data)

# Guardar el DataFrame en un archivo Excel en una ruta específica
try:
    df.to_excel('C:/Users/rreyess/Desktop/vehiculos_tattersall.xlsx', index=False)
    print("Datos guardados en 'vehiculos_tattersall.xlsx'")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")
print(f"Total de páginas recorridas: {page_count}")
