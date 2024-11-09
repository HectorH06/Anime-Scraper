from bs4 import BeautifulSoup as bs
import requests
import os
import re
import subprocess
from dotenv import load_dotenv

# Massive download

login_url = "https://anitaku.bz/login.html"

# Diccionario con base_url como clave y el nombre de la serie como valor
series_dict = {
    "https://anitaku.bz/category/spy-kyoushitsu": "Spy_Kyoushitsu",
    "https://anitaku.bz/category/spy-kyoushitsu-2nd-season": "Spy_Kyoushitsu2",
    "https://anitaku.bz/category/isekai-nonbiri-houka": "Isekai_Nonbiri_Nouka",
    "https://anitaku.bz/category/kage-no-jitsuryokusha-ni-naritakute": "Kage_no_Jitsuryokusha",
    "https://anitaku.bz/category/kage-no-jitsuryokusha-ni-naritakute-2nd-season": "Kage_no_Jitsuryokusha2",
    "https://anitaku.bz/category/fantasy-bishoujo-juniku-ojisan-to": "Fantasy_Bishoujo",
    "https://anitaku.bz/category/koori-zokusei-danshi-to-cool-na-douryou-joshi": "Koori_Zokusei_Danshi",
    "https://anitaku.bz/category/otonari-ni-ginga": "Otonari_ni_Ginga",
    "https://anitaku.bz/category/liar-liar": "Liar_Liar",
    "https://anitaku.bz/category/one-room-hiatari-futsuu-tenshi-tsuki": "One_Room,_Hiatari_Futsuu,_Tenshi-tsuki",
    "https://anitaku.bz/category/shin-no-nakama-ja-nai-to-yuusha-no-party-wo-oidasareta-node-henkyou-de-slow-life-suru-koto-ni-shimashita": "Shin_no_Nakama_ja_nai_to_Yuusha",
    "https://anitaku.bz/category/shin-no-nakama-ja-nai-to-yuusha-no-party-wo-oidasareta-node-henkyou-de-slow-life-suru-koto-ni-shimashita-2nd": "Shin_no_Nakama_ja_nai_to_Yuusha2",
    "https://anitaku.bz/category/temple": "Temple",
    "https://anitaku.bz/category/temple-specials": "Temple_Specials",
    "https://anitaku.bz/category/kami-wa-game-ni-ueteiru": "Kami_wa_Game_ni_Ueteiru",
    "https://anitaku.bz/category/bartender-kami-no-glass": "Bartender-Kami_no_Glass"
}

load_dotenv('.secrets')

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
file_path = os.getenv('FILE_PATH')

quality = 4
firstep = 1
lastep = 20
idm = True # Sin idm, 5 episodios de máxima calidad tardan aproximadamente 15 minutos, con IDM tardan aproximadamente 3 minutos
epiString = True

episodios_descargas = {}

def transformar_url(url_base, numero_episodio):
    url_modificada = re.sub(r"/category", "", url_base)
    if(epiString):
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

if "Logout" in login_response.text:
    print("Login exitoso!")
    
    for base_url, serie in series_dict.items():
        episodios_descargas = {}
        
        print(f"\nDescargando episodios de la serie: {serie}")
        
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

        # Función de descarga con IDM
        def descargar_con_idm(episodios_dict):
            idm_path = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"  # Ruta de IDM, ajusta si es necesario
            if not os.path.exists(idm_path):
                print("IDM no se encontró en la ruta especificada.")
                return
            
            for episodio, url_descarga in episodios_dict.items():
                if url_descarga:
                    numero_episodio = re.search(r'-episode-(\d+)(?!.*\d)', episodio).group(1)
                    file_name = f"{serie}_Episode_{numero_episodio}.mp4"
                    file_full_path = os.path.join(file_path, file_name)
                    
                    print(f"Descargando {file_name} desde {url_descarga} ...")
                    
                    subprocess.run([idm_path, "/d", url_descarga, "/p", file_path, "/f", file_name, "/n", "/a"])
            
            # Comienza todas las descargas agregadas a la cola
            subprocess.run([idm_path, "/s"])
            print("Todas las descargas se han añadido a IDM.")

        if idm:
            descargar_con_idm(episodios_descargas)
        else:
            # Aquí puedes agregar una función para descargar sin IDM si lo prefieres
            pass

else:
    print("Error en el login")
