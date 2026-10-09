import io
from datetime import datetime, timedelta

import numpy as np
import psycopg2
import urllib3
from pypdf import PdfReader
import re
import tabula
import requests
from bs4 import BeautifulSoup
import ssl
import time
import regex

from bolsainterinosclm.settings import env

URL_PATH = f"https://www.educa.jccm.es/es/bolsatra/adjudicacion-plazas-docentes-carta/asignacion-02-05-2025-cuerpos-maestros-ensenanzas-medias"


def log(text, level="INFO"):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [{level}] - {text}")


def open_database():
    conn = None
    try:
        conn = psycopg2.connect(
            host=env("DB_HOST"),
            database=env("DB_NAME"),
            user=env("DB_USER"),
            password=env("DB_PASSWORD"),
            port=env("DB_PORT")
        )
        conn.set_session(autocommit=True)
        log("Base de datos iniciada con éxito.")
    except Exception as error:
        log(f"Error al iniciar la base de datos: {str(error)}", "ERROR")
    return conn


def check_row_types(row):
    if row["Orden"].isdecimal():
        if isinstance(row["DNI"], str):
            if isinstance(row["Tipo Bolsa"], str):
                if isinstance(row["Orden Bolsa"], str):
                    return True
    return False


def get_adjudicados():
    response = {}
    log("Obteniendo candidatos adjudicados.")

    page = requests.get(URL_PATH, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")

    for element in soup.find_all("li", class_="cmResourceList"):
        if element.find("span", class_="resourceData2", string=re.compile("^aspirantes adjudicados", re.IGNORECASE)):
            for path in element.findAll("a", href=True):
                PATH = f"https://www.educa.jccm.es{path['href']}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
                request_response = requests.get(url=PATH, headers=headers, timeout=120, verify=False)
                on_fly_mem_obj = io.BytesIO(request_response.content)
                reader = PdfReader(on_fly_mem_obj)

                cuerpo_id = None
                for i, page in enumerate(reader.pages, start=1):
                    parts = []

                    def visitor_body(text, cm, tm, font_dict, font_size):
                        y = tm[5]
                        if 70 < y < 490:
                            parts.append(text)

                    page.extract_text(visitor_text=visitor_body)
                    for fila in "".join(parts).split("\n"):
                        if fila:
                            if re.match(r'.*[*]{3}[0-9]{4}[*]{2}.*', fila, flags=re.IGNORECASE):
                                dni_nombre_re = regex.findall(r'([*]{3}[\d ]+[*]{2})-([\p{L} \-,\.]+)', fila)
                                if len(dni_nombre_re):
                                    dni = str(dni_nombre_re[0][0]).strip()
                                    nombre = str(dni_nombre_re[0][1]).strip()

                                    if dni and nombre:
                                        if dni in response:
                                            response[dni].append(nombre)
                                        else:
                                            response[dni] = [nombre]

    log("Candidatos adjudicados obtenidos.")
    return response


def main():
    start = time.time()
    INSERTS_LIST = []
    error = False
    conn = open_database()

    if conn:
        date_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # date_time_str = "2025-05-16 14:00:00"

        ADJUDICADOS = get_adjudicados()

        page = requests.get(URL_PATH, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")

        for element in soup.find_all("li", class_="cmResourceList"):
            if element.find("span", class_="resourceData2", string=re.compile("(interinos|aspirantes) disponibles", re.IGNORECASE)):
                pdfs_paths_list = element.findAll("a", href=True)
                for path in pdfs_paths_list:
                    start = time.time()
                    PATH = f"https://www.educa.jccm.es{path['href']}"
                    print(f"- Fichero: {PATH}")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'
                    }
                    response = requests.get(url=PATH, headers=headers, timeout=120, verify=False)
                    on_fly_mem_obj = io.BytesIO(response.content)
                    reader = PdfReader(on_fly_mem_obj)

                    posicion_esp = 1
                    last_especialidad = None
                    for i in range(len(reader.pages)):
                        print(f"({i}/{len(reader.pages)}) - {round(i / len(reader.pages) * 100, 2)}% ")

                        page = reader.pages[i]
                        page_text = page.extract_text().split("\n")

                        fecha = cuerpo = especialidad = None
                        for line in page_text:
                            if "FECHA PUBLICACIÓN" in line:
                                object_re = re.findall(r"[0-9]{1,4}[\_|\-|\/|\|][0-9]{1,2}[\_|\-|\/|\|][0-9]{1,4}", line)
                                if object_re and len(object_re):
                                    date_obj = datetime.strptime(object_re[0], "%d/%m/%Y")
                                    fecha = date_obj.strftime("%Y-%m-%d")

                            if "CUERPO" in line:
                                object_re = re.findall(r"-([0-9]{4})-", line)
                                if object_re and len(object_re):
                                    cuerpo = object_re[0]

                            if "Bolsa" in line:
                                object_re = re.findall(r"[0-9]{3}", line)
                                if object_re and len(object_re) and cuerpo:
                                    cursor_especialidad = None
                                    try:
                                        cursor_especialidad = conn.cursor()
                                        cursor_especialidad.execute(
                                            f"SELECT id FROM api_especialidad WHERE codigo = {object_re[0]} and cuerpo_id = {cuerpo.lstrip('0')}")
                                        for id in cursor_especialidad.fetchall():
                                            if last_especialidad and id[0] != last_especialidad:
                                                posicion_esp = 1
                                            especialidad = id[0]
                                            last_especialidad = id[0]
                                    except Exception as error:
                                        print(f"Error al buscar la especialidad. Info: {str(error)}")
                                    finally:
                                        if cursor_especialidad is not None:
                                            cursor_especialidad.close()

                        if fecha is not None and cuerpo is not None and especialidad is not None:
                            dfs = tabula.read_pdf((PATH), pages=i + 1, area=[[125, 3.9, 745.48, 547.61]],
                                                  pandas_options={'header': None,
                                                                  'columns': ['Orden', 'DNI', 'Apellidos, Nombre',
                                                                              'Tipo Bolsa', 'Orden Bolsa', 'Provincia',
                                                                              'Inglés', 'Francés', 'Alemán',
                                                                              'Italiano']},
                                                  columns=[34, 77, 289, 316, 342, 422, 447, 481, 509, 539])

                            for page_data in dfs:
                                page_data = page_data.dropna(subset=['Orden', 'Orden Bolsa']).reset_index(drop=True)
                                page_data = page_data.replace(np.nan, None)

                                for index, row in page_data.iterrows():
                                    split_nombre = []
                                    nombre = None
                                    apellidos = None

                                    if row['Apellidos, Nombre']:
                                        split_nombre = row['Apellidos, Nombre'].split(",")

                                        if len(split_nombre) > 1:
                                            nombre = split_nombre[1].strip()
                                            apellidos = split_nombre[0].strip()
                                        else:
                                            print(f"[!] Nombre mal formado (sin coma) en página {i + 1}: {row}")
                                    else:
                                        print(f"[!] Falta el campo 'Apellidos, Nombre' en página {i + 1}: {row}")

                                    if check_row_types(row):
                                        if 'DNI' in row:
                                            if row['DNI'] in ADJUDICADOS and nombre and apellidos and row['Apellidos, Nombre'] in ADJUDICADOS[row['DNI']]:
                                                INSERTS_LIST.append(
                                                    [
                                                        None,
                                                        row['DNI'],
                                                        nombre if nombre else "",
                                                        apellidos if apellidos else "",
                                                        row['Tipo Bolsa'],
                                                        row['Orden Bolsa'],
                                                        True if (row['Inglés']) else False,
                                                        True if (row['Francés']) else False,
                                                        True if (row['Alemán']) else False,
                                                        True if (row['Italiano']) else False,
                                                        row['Provincia'].replace(" ", "") if row['Provincia'] else "",
                                                        especialidad,
                                                        fecha,
                                                        date_time_str,
                                                        date_time_str,
                                                        False,
                                                        True
                                                    ]
                                                )
                                            else:
                                                INSERTS_LIST.append(
                                                    [
                                                        posicion_esp,
                                                        row['DNI'],
                                                        nombre if nombre else None,
                                                        apellidos if apellidos else None,
                                                        row['Tipo Bolsa'],
                                                        row['Orden Bolsa'],
                                                        True if (row['Inglés']) else False,
                                                        True if (row['Francés']) else False,
                                                        True if (row['Alemán']) else False,
                                                        True if (row['Italiano']) else False,
                                                        row['Provincia'].replace(" ", "") if row['Provincia'] else "",
                                                        especialidad,
                                                        fecha,
                                                        date_time_str,
                                                        date_time_str,
                                                        False if nombre else True,
                                                        False
                                                    ]
                                                )
                                                posicion_esp += 1
                                    else:
                                        print(f"Error en los tipos de alguno de los atributos en la página {i + 1}. Info: {row}")
                        else:
                            print(f"Error en la fecha, cuerpo o especialidad de la página {i + 1}. Info: {row}")

        if not error:
            cursor = conn.cursor()
            try:
                cursor.executemany(
                    """INSERT INTO api_registro(orden, dni, nombre, apellidos, tipo_bolsa, orden_bolsa, ingles, frances, aleman, italiano, provincias, especialidad_id, fecha, fecha_creacion, fecha_modificacion, error, adjudicado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    INSERTS_LIST
                )

                conn.commit()
                log(f"{len(INSERTS_LIST)} registros insertados correctamente.")
            except Exception as error:
                conn.rollback()
                log(f"Error al insertar registros. Rollback ejecutado. Info: {str(error)}", "ERROR")
            finally:
                cursor.close()

        end = time.time()
        elapsed = end - start
        formatted_time = str(timedelta(seconds=elapsed))

        print(f"- Tiempo: {formatted_time}\n")


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib3.disable_warnings()
    main()
