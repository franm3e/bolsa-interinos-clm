function init() {
    $(document).ready(function () {
        let debounceTimeout;

        $('#busqueda').on('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
            }
        });

        $('#busqueda').on('input', function () {
            clearTimeout(debounceTimeout);

            debounceTimeout = setTimeout(() => {
                const texto = $(this).val().toLowerCase();
                const sugerencias = $('#sugerencias');
                sugerencias.empty();

                if (texto.length === 0) {
                  sugerencias.addClass('d-none');
                } else {
                    $('#spinner-busqueda').removeClass('d-none');
                    fetch(`${API_BASE_URL}api/registro-persona/?search=${texto}&format=json`)
                    .then(response => response.json())
                    .then((data) => {
                        if (data.length === 0) {
                            sugerencias.addClass('d-none');
                        } else {
                            sugerencias.empty();
                            data.forEach(item => {
                                sugerencias.append(`<li class="list-group-item list-group-item-action d-flex justify-content-between align-items-start" data-nombre="${item.nombre}" data-apellidos="${item.apellidos}" data-dni="${item.dni}">
                                    <div class="ms-2 me-auto">
                                        <div>${item.nombre}, ${item.apellidos}</div>
                                    </div>
                                    <small class="text-secondary">${item.dni}</small>
                                </li>`);
                            });

                            sugerencias.removeClass('d-none');
                        }
                    })
                    .catch(error => {
                        console.error("Error en la búsqueda:", error);
                    })
                    .finally(() => {
                        $('#spinner-busqueda').addClass('d-none');
                    });
                }
            }, 800);
        });

        $('#sugerencias').on('click', 'li', function () {
            const nombre = $(this).data('nombre');
            const apellidos = $(this).data('apellidos');
            const dni = $(this).data('dni');

            $('#busqueda').val(nombre + ' ' + apellidos);
            $('#sugerencias').addClass('d-none');

            const params = new URLSearchParams({
                nombre: nombre,
                apellidos: apellidos,
                dni: dni
            });

            window.location.href = `/detalle-interino?${params.toString()}`
        });

        $(document).on('click', function (e) {
        if (!$(e.target).closest('#busqueda, #sugerencias').length) {
            $('#sugerencias').addClass('d-none');
        }
        });
    });
}


function mostrarSpinnerBusqueda(mostrar) {
    if (mostrar) {
        $('#spinner-busqueda').removeClass('d-none');
    } else {
        $('#spinner-busqueda').addClass('d-none');
    }
}


init();