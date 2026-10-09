import { CONFIG_PROVINCIAS } from "./constants.js";

function init() {
    $(document).ready(function () {
        calcularRuta("Albacete", "La Gineta");


        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

        const body = document.body;
        const dni = body.dataset.dni;
        const nombre = body.dataset.nombre;
        const apellidos = body.dataset.apellidos;
        const cuerpo = body.dataset.cuerpo;
        const especialidad = body.dataset.especialidad;
        const fecha = body.dataset.fecha;

        const selectFechas = $('#actualizacion-select');

        let requests = [];

        requests.push(
            fetch(`${API_BASE_URL}api/fechas-registros?dni=${dni}&nombre=${nombre}&apellidos=${apellidos}&format=json`)
            .then(response => response.json())
            .then((data) => {
                selectFechas.empty();
                $('#fechasSpinner').addClass('d-none');

                data.forEach(item => {
                    const [dia, mes, anio] = item.fecha.split("/");

                    const option = $('<option>', {
                        value: `${anio}-${mes}-${dia}`,
                        text: `${item.fecha}${item.adjudicado ? ' (ADJUDICADO)' : ''}`
                    });
                    selectFechas.append(option);
                });

                if (fecha) {
                    selectFechas.val(fecha);
                }

                return fetch(`${API_BASE_URL}api/especialidades-registro?fecha=${selectFechas.val()}&dni=${dni}&nombre=${nombre}&apellidos=${apellidos}&format=json`);
            })
            .then(res => res.json())
            .then((data) => {
                const selectEspecialidad = $('#especialidad-select');

                selectEspecialidad.empty();
                $('#especialidadesSpinner').addClass('d-none');

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.id,
                        text: `${item.nombre} (${item.codigo})`
                    });
                    selectEspecialidad.append(option);
                });

                if (especialidad !== '' && selectEspecialidad.find(`option[value='${especialidad}']`).length > 0) {
                    selectEspecialidad.val(`${especialidad}`).trigger('change');
                }

                $('#especialidad-select').on('change', function () {
                    $('.toggle-posicion').toggleClass('d-none');

                    const selectEspecialidad = $('#especialidad-select');
                    const selectFechas = $('#fechas-select');

                    update_provincias_table(nombre, apellidos, dni, selectEspecialidad.val(), selectFechas.val());
                });

                return update_provincias_table(nombre, apellidos, dni, selectEspecialidad.val(), selectFechas.val());
            })
        );

        requests.push(
            fetch(`${API_BASE_URL}api/registros?dni=${dni}&nombre=${nombre}&apellidos=${apellidos}&format=json`).then(res => res.json())
        );

        Promise.all(requests).then(([data1, dataRegistro]) => {
            const divIdiomas = $('#div-idiomas');
            divIdiomas.html = 'No'

            const idiomas = {
                ingles: "gb",
                aleman: "de",
                italiano: "it",
                frances: "fr"
            };

            dataRegistro = dataRegistro.length > 0 ? dataRegistro[0] : [];

            Object.entries(idiomas).forEach(([idioma, codigoBandera]) => {

                if (dataRegistro[idioma]) {
                    const img = `
                        <img
                        src="https://flagcdn.com/20x15/${codigoBandera}.png"
                        srcset="https://flagcdn.com/40x30/${codigoBandera}.png 2x, https://flagcdn.com/60x45/${codigoBandera}.png 3x"
                        alt="${idioma}"
                        class="ms-1"
                        width="20"
                        height="15"
                        />
                    `;
                    divIdiomas.append(img);
                }
            });
        })
        .catch(error => {
            console.error("Error en alguno de los procesos:", error);
        });

        $('#actualizacion-select').on('change', function () {
            cambiar_estado_select(true);
            $('.toggle-posicion').toggleClass('d-none');

            const selectFechas = $('#actualizacion-select');

            $('#especialidadesSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/especialidades-registro?fecha=${selectFechas.val()}&dni=${dni}&nombre=${nombre}&apellidos=${apellidos}&format=json`)
            .then(response => response.json())
            .then((data) => {
                const selectEspecialidad = $('#especialidad-select');

                selectEspecialidad.empty();
                $('#especialidadesSpinner').addClass('d-none');

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.id,
                        text: `${item.nombre} (${item.codigo})`
                    });
                    selectEspecialidad.append(option);
                });

                return update_provincias_table(nombre, apellidos, dni, selectEspecialidad.val(), selectFechas.val());
            })
            .catch((error) => {
                console.log("Hubo un problema con la petición Fetch:" + error.message);
            })
            .finally(() => {
                cambiar_estado_select(false);
            });
        });

        if (especialidad) {
            $('#div-volver-btn').on('click', function() {
                let fecha = $('#actualizacion-select').val();
                let especialidad = $('#especialidad-select').val();

                window.location.href = `/?version=2024/25&cuerpo=${cuerpo}&especialidad=${especialidad}&fecha=${fecha}`;
            });

            $('#div-volver').removeClass('d-none');
        }
    });
}

var count = 200;
var defaults = {
  origin: { y: 0.7 }
};

function fire(particleRatio, opts) {
    confetti({
        ...defaults,
        ...opts,
        particleCount: Math.floor(count * particleRatio)
    });
}

function cambiar_estado_select(disabled) {
    $('#actualizacion-select').prop('disabled', disabled);
    $('#especialidad-select').prop('disabled', disabled);
}


function tiempoRestante(fechaStr) {
    const [dia, mes, anio] = fechaStr.split("/").map(Number);
    const fechaDestino = new Date(anio, mes - 1, dia);
    const hoy = new Date();

    if (fechaDestino < hoy) return "";

    let years = fechaDestino.getFullYear() - hoy.getFullYear();
    let months = fechaDestino.getMonth() - hoy.getMonth();
    let days = fechaDestino.getDate() - hoy.getDate();

    if (days < 0) {
        months -= 1;
        const ultimoDiaMesAnterior = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0).getDate();
        days += ultimoDiaMesAnterior;
    }
    if (months < 0) {
        years -= 1;
        months += 12;
    }

    const partes = [];
    if (years > 0) partes.push(`${years} ${years === 1 ? 'año' : 'años'}`);
    if (months > 0) partes.push(`${months} ${months === 1 ? 'mes' : 'meses'}`);
    if (days > 0) partes.push(`${days} ${days === 1 ? 'día' : 'días'}`);

    if (partes.length === 0) return "";

    let texto;
    if (partes.length === 1) {
        texto = partes[0];
    } else if (partes.length === 2) {
        texto = partes.join(" y ");
    } else {
        texto = partes.slice(0, -1).join(", ") + " y " + partes[partes.length - 1];
    }

    return `Faltan ${texto}`;
}


function update_provincias_table(nombre, apellidos, dni, especialidad, fecha) {
    const selectFechas = $('#actualizacion-select');
    let requests = [];

    requests.push(
        fetch(`${API_BASE_URL}api/orden-especialidad-provincia/?fecha=${selectFechas.val()}&&dni=${dni}&nombre=${nombre}&apellidos=${apellidos}&especialidad=${especialidad}&format=json`).then(response => response.json())
    );

    Promise.all(requests).then(([ordenEspecialidadResponse]) => {
        const tablaPosiciones = $('#tabla-posiciones').get(0);
        tablaPosiciones.innerHTML = '';

        const tbody_idiomas = document.querySelector('#tabla-posiciones-idiomas tbody');
        tbody_idiomas.innerHTML = '';

        ordenEspecialidadResponse.forEach(item => {
            $('#posicion-bolsa-general').html(`<span class="text-primary">${item.posicion_bolsa_general}</span><small class="text-secondary"> / ${item.total_bolsa_general}</small>`);

            if (item.posicion_general_especialidad) {
                $('#posicion-general-especialidad').html(`<span class="text-primary">${item.posicion_general_especialidad}</span><small class="text-secondary"> / ${item.total_general_especialidad}</small>`);
                item.posicion_provincias.forEach(provincia => {
                    const cardHTML = `
                        <div class="card mb-3" style="background-color: ${CONFIG_PROVINCIAS[provincia.provincia.nombre].color}; border: 1px solid ${CONFIG_PROVINCIAS[provincia.provincia.nombre].border};">
                            <div class="card-body d-flex justify-content-between align-items-center py-2">
                                <div class="d-flex align-items-center">
                                    <div class="d-flex flex-column">
                                        <span class="fw-bold text-dark">${provincia.provincia.nombre}</span>
                                        <small>Fecha estimada: ${provincia.fecha_estimada}</small>
                                        <small>${provincia.posicion_solo_provincia} tienen solo esta provincia</small>
                                    </div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div style="
                                        width: 90px;
                                        height: 40px;
                                        background-color: white;
                                        color: ${CONFIG_PROVINCIAS[provincia.provincia.nombre].text};
                                        border-radius: 0.5rem;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        box-shadow: 0 0 6px rgba(0,0,0,0.2);
                                        font-weight: bold;
                                        margin-right: 8px;
                                    ">
                                    ${provincia.posicion} <small class="text-success ms-1" style="font-size: 12px; font-weight: normal;">${ (provincia.alteracion === 0 || provincia.alteracion === null) ? "" : ((provincia.alteracion < 0) ? `<i class="bi bi-arrow-up text-success"></i>${Math.abs(provincia.alteracion)}` : `<i class="bi bi-arrow-down text-danger"></i>${Math.abs(provincia.alteracion)}`) }</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;

                    tablaPosiciones.insertAdjacentHTML("beforeend", cardHTML);

                    const tr_idiomas = document.createElement('tr');

                    tr_idiomas.innerHTML = `
                        <td>${provincia.provincia.nombre}</td>
                        <td style="white-space: nowrap; width: 1%;" class="text-primary-emphasis text-center align-middle ${provincia.posicion_idioma_provincia.ingles.habilitado ? 'table-primary' : ''}">${provincia.posicion_idioma_provincia.ingles.posicion}</td>
                        <td style="white-space: nowrap; width: 1%;" class="text-primary-emphasis text-center align-middle ${provincia.posicion_idioma_provincia.frances.habilitado ? 'table-primary' : ''}">${provincia.posicion_idioma_provincia.frances.posicion}</td>
                        <td style="white-space: nowrap; width: 1%;" class="text-primary-emphasis text-center align-middle ${provincia.posicion_idioma_provincia.italiano.habilitado ? 'table-primary' : ''}">${provincia.posicion_idioma_provincia.italiano.posicion}</td>
                        <td style="white-space: nowrap; width: 1%;" class="text-primary-emphasis text-center align-middle ${provincia.posicion_idioma_provincia.aleman.habilitado ? 'table-primary' : ''}">${provincia.posicion_idioma_provincia.aleman.posicion}</td>
                    `;

                    tbody_idiomas.appendChild(tr_idiomas);
                });

                $('#div-posiciones').removeClass('d-none');
                $('#div-adjudicado').addClass('d-none');
            } else {
                fire(0.25, {
                    spread: 26,
                    startVelocity: 55,
                });
                fire(0.2, {
                    spread: 60,
                });
                fire(0.35, {
                    spread: 100,
                    decay: 0.91,
                    scalar: 0.8
                });
                fire(0.1, {
                    spread: 120,
                    startVelocity: 25,
                    decay: 0.92,
                    scalar: 1.2
                });
                fire(0.1, {
                    spread: 120,
                    startVelocity: 45,
                });

                function toTitleCase(texto) {
                    return texto.toLowerCase().split(' ').map((palabra, i) => {
                        if (palabra.length <= 2 && i > 0) {
                            return palabra; // deja en minúscula si tiene 2 letras y no es la primera
                        }
                        return palabra.charAt(0).toUpperCase() + palabra.slice(1);
                    }).join(' ');
                }

                if (item.plaza) {
                    let fecha_desde = new Date(item.plaza.fecha_inicio);
                    let fecha_hasta = new Date(item.plaza.fecha_fin);

                    $("#plaza-centro").text(`${item.plaza.centro.nombre}`);
                    $("#plaza-localidad").html(`<i class="bi bi-geo-alt"></i> ${toTitleCase(item.plaza.centro.localidad)} (${item.plaza.centro.provincia.nombre})`);
                    $("#plaza-telefonos").html(`${(item.plaza.centro.telefono) ? `<a class="link-primary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover" href="tel:+34${item.plaza.centro.telefono}">${item.plaza.centro.telefono}</a>` : ''} ${(item.plaza.centro.movil) ? `<a href="tel:+34${item.plaza.centro.movil}" class="ms-2 link-primary link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">${item.plaza.centro.movil}</a>` : ''}`);
                    $("#plaza-cuerpo").text(`${item.plaza.funcion.especialidad.cuerpo.nombre} (0${item.plaza.funcion.especialidad.cuerpo.codigo})`);
                    $("#plaza-especialidad").text(`${item.plaza.funcion.especialidad.nombre} (0${item.plaza.funcion.especialidad.codigo})`);
                    $("#plaza-funcion").text(`${item.plaza.funcion.nombre}`);
                    $("#plaza-jornada").text(`${item.plaza.jornada}`);
                    $("#plaza-desde").text(`${item.plaza.fecha_inicio}`);
                    $("#plaza-hasta").text(`${item.plaza.fecha_fin}`);
                    $("#plaza-puesto").text(`${item.plaza.puesto}`);
                    $("#plaza-programa").text(`${item.plaza.programa ? item.plaza.programa : ''}`);
                    $("#plaza-competencia").text(`${item.plaza.competencia ? item.plaza.competencia : ''}`);
                }

                $('#div-posiciones').addClass('d-none');
                $('#div-adjudicado').removeClass('d-none');
            }
        });
    }).finally(() => {
        $('.toggle-posicion').toggleClass('d-none');
    });
}


// Función para obtener coordenadas de un lugar con Nominatim
async function geocodeLugar(lugar) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(lugar + ", España")}`;

  const resp = await fetch(url, {
    headers: {
      "User-Agent": "distancia-app/1.0 (tuemail@example.com)" // Nominatim requiere identificar al cliente
    }
  });
  const datos = await resp.json();

  if (datos.length > 0) {
    return {
      lat: parseFloat(datos[0].lat),
      lon: parseFloat(datos[0].lon)
    };
  } else {
    throw new Error("No se encontraron coordenadas para " + lugar);
  }
}

// Función para calcular distancia con OSRM
async function calcularRuta(origen, destino) {
  // Primero geocodificamos ambos
  const coordOrigen = await geocodeLugar(origen);
  const coordDestino = await geocodeLugar(destino);

  const url = `https://router.project-osrm.org/route/v1/driving/${coordOrigen.lon},${coordOrigen.lat};${coordDestino.lon},${coordDestino.lat}?overview=false`;

  const resp = await fetch(url);
  const datos = await resp.json();

  if (datos.routes && datos.routes.length > 0) {
    const distanciaKm = (datos.routes[0].distance / 1000).toFixed(2);
    const duracionMin = (datos.routes[0].duration / 60).toFixed(0);
    console.log(`De ${origen} a ${destino}:`);
    console.log(`Distancia: ${distanciaKm} km`);
    console.log(`Duración: ${duracionMin} min`);
  } else {
    console.log("No se pudo calcular la ruta.");
  }
}



init();