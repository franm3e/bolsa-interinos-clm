import { CONFIG_PROVINCIAS } from "./constants.js";

function init() {
    $(document).ready(function () {
        cambiar_estado_select(true);
        const selectFechas = $('#actualizacion-select');

        fetch(`${API_BASE_URL}api/fechas-plazas?format=json`)
        .then(response => response.json())
        .then((data) => {
            const selectFechas = $('#actualizacion-select');
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

            return fetch(`${API_BASE_URL}api/funciones-plazas?fecha=${selectFechas.val()}&format=json`);
        })
        .then(res => res.json())
        .then((data) => {
            const selectFuncion = $('#funcion-select');
            selectFuncion.empty();

            data.forEach(item => {
                const option = $('<option>', {
                    value: item.codigo,
                    text: `${item.nombre} (${item.codigo})`
                });
                selectFuncion.append(option);
            });

            $('#funcionSpinner').addClass('d-none');

            return fetch(`${API_BASE_URL}api/provincias-plazas?fecha=${selectFechas.val()}&format=json`);
        })
        .then(res => res.json())
        .then((data) => {
            const selectProvincia = $('#provincia-select');
            selectProvincia.empty();
            $('#provinciaSpinner').addClass('d-none');

            data.forEach(item => {
                const option = $('<option>', {
                    value: item.codigo,
                    text: `${item.nombre}`
                });
                selectProvincia.append(option);
            });

            $('#provinciaSpinner').addClass('d-none');

            return fetch(`${API_BASE_URL}api/plazas?fecha=${selectFechas.val()}&format=json`);
        })
        .then(res => res.json())
        .then((data) => {
            const divPlazas = $('#div-plazas');
            const totalPlazas = $('#total-plazas');
            const totalCeses = $('#total-ceses');

            divPlazas.empty();
            totalPlazas.text(data.plazas.length);
            totalCeses.text(data.total_ceses)

            data.plazas.forEach(item => {
                divPlazas.append(`
                    <div class="col">
                        <div class="card" style="background-color: ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].color}; border: 1px solid ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].border};">
                            <div class="card-body">
                                <p class="card-title"><small class="text-body-secondary">${item.funcion.nombre} (${item.funcion.codigo})</small></p>
                                <h5 class="card-title">${item.centro.nombre}</h5>
                                <h6 class="card-subtitle mb-2 text-primary-emphasis"><i class="bi bi-geo-alt"></i> ${toTitleCase(item.centro.localidad)} (${item.centro.provincia.nombre_codigo})</h6>
                                <p class="card-text m-0">${item.jornada} / ${item.puesto}</p>
                                <p class="card-text">${item.fecha_inicio} - ${item.fecha_fin}</p>
                            </div>
                        </div>
                    </div>
                `);
            });
        })
        .catch((error) => {
            console.log("Hubo un problema con la petición Fetch:" + error.message);
        })
        .finally(() => {
            cambiar_estado_select(false);
            $('.toggle-posicion').toggleClass('d-none');
        });


        $('#actualizacion-select').on('change', function () {
            cambiar_estado_select(true);
            $('.toggle-posicion').toggleClass('d-none');


            const selectFechas = $('#actualizacion-select');
            const fecha = selectFechas.val();
            const selectFuncion = $('#funcion-select');
            const selectProvincia = $('#provincia-select');

            $('#funcionSpinner').removeClass('d-none');
            $('#provinciaSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/funciones-plazas?fecha=${fecha}&format=json`)
            .then(response => response.json())
            .then(data => {
                selectFuncion.empty();

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.codigo,
                        text: `${item.nombre} (${item.codigo})`
                    });
                    selectFuncion.append(option);
                });

                $('#funcionSpinner').addClass('d-none');

                return fetch(`${API_BASE_URL}api/provincias-plazas?fecha=${fecha}&format=json`);
            })
            .then(response => response.json())
            .then(data => {
                selectProvincia.empty();

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.codigo,
                        text: `${item.nombre}`
                    });
                    selectProvincia.append(option);
                });

                $('#provinciaSpinner').addClass('d-none');

                return fetch(`${API_BASE_URL}api/plazas?fecha=${selectFechas.val()}&format=json`);
            })
            .then(res => res.json())
            .then((data) => {
                const divPlazas = $('#div-plazas');
                const totalPlazas = $('#total-plazas');
                const totalCeses = $('#total-ceses');

                divPlazas.empty();
                totalPlazas.text(data.plazas.length);
                totalCeses.text(data.total_ceses)

                data.plazas.forEach(item => {
                    divPlazas.append(`
                        <div class="col">
                            <div class="card" style="background-color: ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].color}; border: 1px solid ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].border};">
                                <div class="card-body">
                                    <p class="card-title"><small class="text-body-secondary">${item.funcion.nombre} (${item.funcion.codigo})</small></p>
                                    <h5 class="card-title">${item.centro.nombre}</h5>
                                    <h6 class="card-subtitle mb-2 text-primary-emphasis"><i class="bi bi-geo-alt"></i> ${toTitleCase(item.centro.localidad)} (${item.centro.provincia.nombre_codigo})</h6>
                                    <p class="card-text m-0">${item.jornada} / ${item.puesto}</p>
                                    <p class="card-text">${item.fecha_inicio} - ${item.fecha_fin}</p>
                                </div>
                            </div>
                        </div>
                    `);
                });
            })
            .catch(error => {
                console.error("Hubo un problema con la petición Fetch:", error.message);
            })
            .finally(() => {
                cambiar_estado_select(false);
                $('.toggle-posicion').toggleClass('d-none');
            });
        });

        $('#funcion-select').on('change', function () {
            cambiar_estado_select(true);
            $('.toggle-posicion').toggleClass('d-none');

            const selectFechas = $('#actualizacion-select');
            const fecha = selectFechas.val();
            const selectFuncion = $('#funcion-select');
            const selectProvincia = $('#provincia-select');

            $('#funcionSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/plazas?fecha=${selectFechas.val()}&funciones=${selectFuncion.val()}&provincias=${selectProvincia.val()}&format=json`)
            .then(response => response.json())
            .then(data => {
                const divPlazas = $('#div-plazas');
                const totalPlazas = $('#total-plazas');
                const totalCeses = $('#total-ceses');

                divPlazas.empty();
                totalPlazas.text(data.plazas.length);
                totalCeses.text(data.total_ceses)

                data.plazas.forEach(item => {
                    divPlazas.append(`
                        <div class="col">
                            <div class="card" style="background-color: ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].color}; border: 1px solid ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].border};">
                                <div class="card-body">
                                    <p class="card-title"><small class="text-body-secondary">${item.funcion.nombre} (${item.funcion.codigo})</small></p>
                                    <h5 class="card-title">${item.centro.nombre}</h5>
                                    <h6 class="card-subtitle mb-2 text-primary-emphasis"><i class="bi bi-geo-alt"></i> ${toTitleCase(item.centro.localidad)} (${item.centro.provincia.nombre_codigo})</h6>
                                    <p class="card-text m-0">${item.jornada} / ${item.puesto}</p>
                                    <p class="card-text">${item.fecha_inicio} - ${item.fecha_fin}</p>
                                </div>
                            </div>
                        </div>
                    `);
                });
            })
            .catch(error => {
                console.error("Hubo un problema con la petición Fetch:", error.message);
            })
            .finally(() => {
                $('#funcionSpinner').addClass('d-none');
                cambiar_estado_select(false);
                $('.toggle-posicion').toggleClass('d-none');
            });
        });

        $('#provincia-select').on('change', function () {
            cambiar_estado_select(true);
            $('.toggle-posicion').toggleClass('d-none');

            const selectFechas = $('#actualizacion-select');
            const fecha = selectFechas.val();
            const selectFuncion = $('#funcion-select');
            const selectProvincia = $('#provincia-select');

            $('#provinciaSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/plazas?fecha=${selectFechas.val()}&funciones=${selectFuncion.val()}&provincias=${selectProvincia.val()}&format=json`)
            .then(response => response.json())
            .then(data => {
                const divPlazas = $('#div-plazas');
                const totalPlazas = $('#total-plazas');
                const totalCeses = $('#total-ceses');

                divPlazas.empty();
                totalPlazas.text(data.plazas.length);
                totalCeses.text(data.total_ceses)

                data.plazas.forEach(item => {
                    divPlazas.append(`
                        <div class="col">
                            <div class="card" style="background-color: ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].color}; border: 1px solid ${CONFIG_PROVINCIAS[item.centro.provincia.nombre].border};">
                                <div class="card-body">
                                    <p class="card-title"><small class="text-body-secondary">${item.funcion.nombre} (${item.funcion.codigo})</small></p>
                                    <h5 class="card-title">${item.centro.nombre}</h5>
                                    <h6 class="card-subtitle mb-2 text-primary-emphasis"><i class="bi bi-geo-alt"></i> ${toTitleCase(item.centro.localidad)} (${item.centro.provincia.nombre_codigo})</h6>
                                    <p class="card-text m-0">${item.jornada} / ${item.puesto}</p>
                                    <p class="card-text">${item.fecha_inicio} - ${item.fecha_fin}</p>
                                </div>
                            </div>
                        </div>
                    `);
                });
            })
            .catch(error => {
                console.error("Hubo un problema con la petición Fetch:", error.message);
            })
            .finally(() => {
                $('#provinciaSpinner').addClass('d-none');
                cambiar_estado_select(false);
                $('.toggle-posicion').toggleClass('d-none');
            });
        });

        $("#filtrar-btn").on("click", function() {
            $("#filtrar-modal").show();
        });

    });
}


function toTitleCase(texto) {
    return texto.toLowerCase().split(' ').map((palabra, i) => {
        if (palabra.length <= 2 && i > 0) {
            return palabra; // deja en minúscula si tiene 2 letras y no es la primera
        }
        return palabra.charAt(0).toUpperCase() + palabra.slice(1);
    }).join(' ');
}


function cambiar_estado_select(disabled) {
    $('#actualizacion-select').prop('disabled', disabled);
    $('#funcion-select').prop('disabled', disabled);
    $('#provincia-select').prop('disabled', disabled);
}

init();