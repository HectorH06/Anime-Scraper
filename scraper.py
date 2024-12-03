import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os
import re
import subprocess
from dotenv import load_dotenv

#region Setup and info extraction
load_dotenv('.secrets')

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
file_path = os.getenv('FILE_PATH')

quality = 4
firstep = 1
lastep = 26
idm = True # Cambia a True si quieres usar IDM, False para usar requests
epiString = True

def cargar_series_dict(ruta_archivo):
    df = pd.read_excel(ruta_archivo, usecols=[0, 1], header=None)
    df[1] = df[1].str.replace(' ', '_')
    series_dict = dict(zip(df[0], df[1]))
    return series_dict

ruta_excel = 'series.xlsx'
series_dict = cargar_series_dict(ruta_excel)

login_url = "https://anitaku.bz/login.html"

episodios_descargas = {}
#endregion

#region Session
def transformar_url(url_base, numero_episodio):
    url_modificada = re.sub(r"/category", "", url_base)
    if epiString:
        episodio_url = f"{url_modificada}-episode-{numero_episodio}"
    else:
        episodio_url = f"{url_modificada}-{numero_episodio}"
    print(episodio_url)
    return episodio_url

session = requests.Session()
login_page = session.get(login_url)
soup = bs(login_page.text, 'html.parser')
csrf_token = soup.find('input', {'name': '_csrf'})['value']

login_data = {
    "email": email,
    "password": password,
    "_csrf": csrf_token,
    "remember": "1"
}

login_response = session.post(login_url, data=login_data)
#endregion

#region IDM
def obtener_links_descarga(session, url):
    response = session.get(url)
    if response.status_code == 200:
        soup = bs(response.content, 'html.parser')
        list_download_div = soup.find('div', class_='list_dowload')
        
        if list_download_div:
            cf_download_div = list_download_div.find('div', class_='cf-download')
            
            if cf_download_div:
                links = [a['href'] for a in cf_download_div.find_all('a', href=True)]
                if 1 <= quality <= len(links):
                    return links[quality - 1]
                else:
                    print("La calidad seleccionada está fuera de rango.")
                    return links[len(links)-1]
            else:
                print("No se encontró el div 'cf-download'.")
        else:
            print("No se encontró el div 'list_dowload'.")
    else:
        print(f"Error al acceder a la página. Código de estado: {response.status_code}")
    return None
#endregion

#region Requests
def descargar_sin_idm(episodios_dict, serie_folder):
    for episodio, url_descarga in episodios_dict.items():
        if url_descarga:
            numero_episodio = re.search(r'-episode-(\d+)(?!.*\d)', episodio).group(1)
            file_name = f"{serie}_Episode_{numero_episodio}.mp4"
            file_full_path = os.path.join(serie_folder, file_name)
            
            print(f"Descargando {file_name} desde {url_descarga} ...")
            
            with requests.get(url_descarga, stream=True) as r:
                r.raise_for_status()
                with open(file_full_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Descarga completa: {file_name}")
#endregion

#region Download
if "Logout" in login_response.text:
    print("Login exitoso!")
    for base_url, serie in series_dict.items():
        episodios_descargas = {}
        print(f"\nDescargando episodios de la serie: {serie}")
        
        # Crear un directorio para la serie
        serie_folder = os.path.join(file_path, serie)
        os.makedirs(serie_folder, exist_ok=True)
        
        for i in range(firstep, lastep + 1):
            episodio_url = transformar_url(base_url, i)
            link_descarga = obtener_links_descarga(session, episodio_url)
            
            if link_descarga:
                episodios_descargas[episodio_url] = link_descarga
                print(f"Episodio {i}: {link_descarga}")
            else:
                episodios_descargas[episodio_url] = None
                print(f"No se encontró un link de descarga para el episodio {i}")
        
        print(f"\nDiccionario de episodios con sus links de descarga para la serie {serie}:")
        print(episodios_descargas)

        if idm:
            def descargar_con_idm(episodios_dict, serie_folder):
                idm_path = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe" 
                if not os.path.exists(idm_path):
                    print("IDM no se encontró en la ruta especificada.")
                    return
                
                for episodio, url_descarga in episodios_dict.items():
                    if url_descarga:
                        numero_episodio = re.search(r'-episode-(\d+)(?!.*\d)', episodio).group(1)
                        file_name = f"{serie}_Episode_{numero_episodio}.mp4"
                        file_full_path = os.path.join(serie_folder, file_name)
                        
                        print(f"Descargando {file_name} desde {url_descarga} ...")
                        
                        subprocess.run([idm_path, "/d", url_descarga, "/p", serie_folder, "/f", file_name, "/n", "/a"])
                
                subprocess.run([idm_path, "/s"])
                print("Todas las descargas se han añadido a IDM.")
            
            descargar_con_idm(episodios_descargas, serie_folder)
        else:
            descargar_sin_idm(episodios_descargas, serie_folder)

else:
    print("Error en el login")
#endregion
