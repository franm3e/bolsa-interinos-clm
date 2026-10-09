import io
from datetime import datetime
import psycopg2
import urllib3
from pypdf import PdfReader
import re
import requests
from bs4 import BeautifulSoup
import time

from bolsainterinosclm.settings import env

URL_PATH = "https://www.educa.jccm.es/es/bolsatra/adjudicacion-plazas-docentes-carta/plazas-disponibles-cuerpos-maestros-eemm-objeto-adjudica-16"
RE_TIPO_CONTRATO = r"ORDINARIO|ITINERANTE"
RE_TIPO_JORNADA = r"JORNADA COMPLETA|1/3 DE JORNADA|1/2 DE JORNADA|16 HORAS SEMANALES"


def log_info(text, space=False):
    log(text, "INFO", space)


def log_error(text, space=False):
    log(text, "ERROR", space)


def log(text, level="INFO", space=False):
    if space:
        print()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [{level}] - {text}")


def open_database():
    conn = None

    try:
        conn = psycopg2.connect(
            host=env("DB_HOST"),
            database=env("DB_NAME"),
            user=env("DB_USER"),
            password=env("DB_PASSWORD"),
            port=env("DB_PORT"),
        )
        log_info("Base de datos iniciada con éxito.")
    except Exception as error:
        log_error(f"Error al iniciar la base de datos: {str(error)}")
    return conn


def main():
    inserts_list = []
    error = False
    conn = open_database()

    if conn:
        date_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_time_str = "2025-05-09 14:00:00"

        page = requests.get(URL_PATH, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")

        for element in soup.find_all("li", class_="cmResourceList"):
            if element.find("span", class_="resourceData2", string=re.compile("^plazas disponibles", re.IGNORECASE)):
                for path in element.findAll("a", href=True):
                    start = time.time()
                    PATH = f"https://www.educa.jccm.es{path['href']}"
                    log_info(f"Fichero: {PATH}", True)
                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
                    response = requests.get(url=PATH, headers=headers, timeout=120, verify=False)
                    on_fly_mem_obj = io.BytesIO(response.content)
                    reader = PdfReader(on_fly_mem_obj)

                    fecha_inicio = fecha_fin = especialidad_id = funcion_id = centro_id = programa_id = datos_re_pl = datos_re_sl = cuerpo_id = None
                    for i, page in enumerate(reader.pages, start=1):
                        log_info(f"({i}/{len(reader.pages)}) - {round(i / len(reader.pages) * 100, 2)}% ", True)

                        parts = []
                        def visitor_body(text, cm, tm, font_dict, font_size):
                            y = tm[5]
                            if 70 < y < 490:
                                parts.append(text)

                        page_text = page.extract_text(visitor_text=visitor_body)

                        if not cuerpo_id:
                            cuerpo_re = re.findall(r'CUERPO\s*-([\d ]*)-.*', page_text, flags=re.IGNORECASE)
                            if cuerpo_re:
                                cuerpo_id = int(cuerpo_re[0])

                        for index, fila in enumerate("".join(parts).split("\n")):
                            if fila and not re.match(r'^Centro.*', fila, flags=re.IGNORECASE):
                                log_info(fila)

                                if re.match(r'^Especialidad.*', fila, flags=re.IGNORECASE):
                                    especialidad_id = None

                                    especialidad_re = re.findall(r'^Especialidad([\w :().]*)$', fila, flags=re.IGNORECASE)
                                    if especialidad_re:
                                        especialidad_nombre = str(especialidad_re[0]).strip()

                                        cursor = None
                                        try:
                                            cursor = conn.cursor()
                                            cursor.execute(f"SELECT id FROM api_especialidad WHERE cuerpo_id = {cuerpo_id} AND unaccent(nombre) iLIKE unaccent('{especialidad_nombre}')")

                                            if cursor.rowcount:
                                                for row in cursor:
                                                    especialidad_id = row[0]

                                        except Exception as error:
                                            log_error(f"Error al buscar el código de especialidad. Info: {str(error)}")
                                        finally:
                                            if cursor is not None:
                                                cursor.close()

                                elif re.match(r'^Función', fila, flags=re.IGNORECASE):
                                    funcion_id = None

                                    funcion_re = re.findall(r'^Función- ([\d]+) ([\w ]*)', fila, flags=re.IGNORECASE)
                                    if funcion_re:
                                        funcion_codigo = int(funcion_re[0][0])
                                        funcion_nombre = str(funcion_re[0][1]).strip()

                                        cursor = None
                                        try:
                                            cursor = conn.cursor()
                                            cursor.execute(f"SELECT id FROM api_funcion WHERE codigo = {funcion_codigo}")

                                            if cursor.rowcount:
                                                for row in cursor:
                                                    funcion_id = row[0]
                                            else:
                                                cursor.execute(
                                                    "INSERT INTO api_funcion(codigo, nombre, especialidad_id, fecha_creacion, fecha_modificacion) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                                                    (
                                                        funcion_codigo,
                                                        funcion_nombre,
                                                        especialidad_id,
                                                        date_time_str,
                                                        date_time_str
                                                    )
                                                )

                                                funcion_id = cursor.fetchone()[0]
                                                conn.commit()
                                        except Exception as error:
                                            log_error(f"Error al buscar o crear el código de función. Info: {str(error)}")
                                        finally:
                                            if cursor is not None:
                                                cursor.close()

                                else:
                                    if re.match(r'.*(\d{2}\/\d{2}\/\d{4}).*', fila):
                                        datos_re_sl = re.findall(r'^(.*)(\d{2}\/\d{2}\/\d{4}) (\d{2}\/\d{2}\/\d{4})([\d ]*)?', fila, flags=re.IGNORECASE)[0]

                                        if datos_re_pl and datos_re_sl:
                                            cursor = None
                                            try:
                                                cursor = conn.cursor()

                                                cursor.execute(
                                                    f"SELECT id FROM api_centro WHERE codigo = {datos_re_pl[0]}"
                                                )

                                                if cursor.rowcount:
                                                    for row in cursor:
                                                        centro_id = row[0]
                                                else:
                                                    cursor.execute(
                                                        "INSERT INTO api_centro(codigo, nombre, localidad, fecha_creacion, fecha_modificacion) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                                                        (
                                                            datos_re_pl[0],
                                                            datos_re_sl[0],
                                                            datos_re_pl[1],
                                                            date_time_str,
                                                            date_time_str
                                                        )
                                                    )

                                                    centro_id = cursor.fetchone()[0]
                                                    conn.commit()

                                                if datos_re_sl[3]:
                                                    cursor.execute(
                                                        f"SELECT id FROM api_programa WHERE codigo = {datos_re_sl[3]}"
                                                    )

                                                    if cursor.rowcount:
                                                        for row in cursor:
                                                            programa_id = row[0]
                                                    else:
                                                        cursor.execute(
                                                            "INSERT INTO api_programa(codigo, fecha_creacion, fecha_modificacion) VALUES (%s, %s, %s) RETURNING id",
                                                            (
                                                                datos_re_sl[3],
                                                                date_time_str,
                                                                date_time_str
                                                            )
                                                        )

                                                        programa_id = cursor.fetchone()[0]
                                                        conn.commit()

                                                if datos_re_sl and len(datos_re_sl) > 2:
                                                    fecha_inicio = datetime.strptime(datos_re_sl[1], "%d/%m/%Y").strftime("%Y-%m-%d")
                                                    fecha_fin = datetime.strptime(datos_re_sl[2], "%d/%m/%Y").strftime("%Y-%m-%d")

                                                if especialidad_id and datos_re_pl[3]:
                                                    inserts_list.append(
                                                        [
                                                            datos_re_pl[2],
                                                            datos_re_pl[3],
                                                            datos_re_pl[4],
                                                            fecha_inicio,
                                                            fecha_fin,
                                                            centro_id,
                                                            programa_id,
                                                            funcion_id,
                                                            False,
                                                            date_time_str,
                                                            date_time_str
                                                        ]
                                                    )
                                                else:
                                                    error = True
                                                    log_error(f"Ha ocurrido un error al insertar un registro. No se encuentra especialidad o jornada no identificada.")

                                                conn.commit()
                                            except Exception as error:
                                                log_error(f"Error al procesar la segunda linea de información. Info: {str(error)}")
                                            finally:
                                                datos_re_pl = centro_id = programa_id = fecha_inicio = fecha_fin = None
                                                if cursor is not None:
                                                    cursor.close()

                                    else:
                                        datos_re_pl = re.findall(r'^(\d+) (.*) (ORDINARIO|ITINERANTE) (JORNADA COMPLETA|[\d\/]+ DE JORNADA|\d+ HORAS SEMANALES)?([\w ]*)?', fila, flags=re.IGNORECASE)
                                        if datos_re_pl:
                                            datos_re_pl = datos_re_pl[0]

        if not error:
            for insert in inserts_list:
                cursor = None
                try:
                    cursor = conn.cursor()

                    cursor.execute(
                        "INSERT INTO api_plaza(puesto, jornada, competencia, fecha_inicio, fecha_fin, centro_id, programa_id, funcion_id, error, fecha_creacion, fecha_modificacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            insert[0],
                            insert[1],
                            insert[2],
                            insert[3],
                            insert[4],
                            insert[5],
                            insert[6],
                            insert[7],
                            insert[8],
                            insert[9],
                            insert[10]
                        )
                    )
                    conn.commit()
                except Exception as error:
                    log_error(f"Error al procesar los insert finales. Hay que hacer rollback!!. Info: {str(error)}")
                finally:
                    if cursor is not None:
                        cursor.close()

    if conn is not None:
        conn.close()


if __name__ == '__main__':
    urllib3.disable_warnings()
    main()

