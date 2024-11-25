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

# URL base para las páginas
base_url = "https://www.kavak.com/cl/usados?page="

# Listas para almacenar datos de todas las páginas
nombres = []
modelos = []
anios = []
kilometrajes = []
modelo2 = []
tipo = []
precios = []

# Contador de páginas
page_count = 1

driver.get(base_url + "1")
time.sleep(5) 
results_element = driver.find_element(By.CLASS_NAME, "results")
results_text = results_element.text.strip()  # Obtener el texto del elemento
max_pages = int(results_text[-2:])  # Extraer los dos últimos caracteres y convertir a entero
print(f"Número máximo de páginas detectado: {max_pages}")


# Bucle para recorrer todas las páginas
while page_count <= max_pages:
    try:
        # Construir la URL de la página actual
        url = base_url + str(page_count)
        print(f"Procesando página: {url}")
        
        driver.get(url)
        time.sleep(5)  # Esperar para la carga de la página
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        Nombre = [element.get_text(strip=True) for element in soup.find_all(class_='card-header')]
        Precio = [element.get_text(strip=True) for element in soup.find_all(class_='price')]
        
        # Procesar cada nombre de auto
        for texto, precio in zip(Nombre, Precio):
            try:
                # Separar el texto por "•"
                partes = [part.strip() for part in texto.split('•')]

                # Validar que haya suficientes partes antes de acceder a índices
                if len(partes) < 5:
                    print(f"Formato inesperado en el texto: {texto}")
                    continue  # Saltar al siguiente si el formato no es válido

                # Separar el modelo y el año
                modelo_año = partes[1]  # Modelo y año
                modelo = modelo_año[:-4]  # Eliminar los últimos 4 caracteres para el modelo
                año = modelo_año[-4:]     # Los últimos 4 caracteres son el año

                # Almacenar en las listas
                nombres.append(partes[0])   
                modelos.append(modelo)      
                modelo2.append(partes[3])  
                anios.append(año)          
                kilometrajes.append(partes[2]) 
                tipo.append(partes[4])      
                precios.append(precio)

            except Exception as e:
                print(f"Error al procesar el texto: {texto}. Error: {e}")
                continue  # Continuar con el siguiente elemento

        # Incrementar el contador para pasar a la siguiente página
        page_count += 1
    
    except Exception as e:
        print(f"Error al procesar la página {page_count}. Error: {e}")
        break

# Crear un DataFrame con los datos recolectados
data = {
    'Marca': nombres,
    'Modelo': modelos,
    'Modelo2': modelo2,
    'Año': anios,
    'Kilometraje': kilometrajes,
    'Tipo': tipo,
    'Precio': precios
}

df = pd.DataFrame(data)


# Guardar los datos en un archivo Excel
try:
    df.to_excel('C:/Users/Pc/Desktop/vehiculos_kavak.xlsx', index=False)
    print("Datos guardados en 'vehiculos_kavak.xlsx'")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")

print(f"Total de páginas recorridas: {page_count - 1}")

# Cerrar el navegador
driver.quit()
