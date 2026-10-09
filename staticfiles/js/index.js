function init() {
    $(document).ready(function () {
        let gridApi = create_aggrid_table();

        const body = document.body;
        const cuerpo = body.dataset.cuerpo;
        const especialidad = body.dataset.especialidad;
        const fecha = body.dataset.fecha;

        $('#actualizacion-select').on('change', function () {
            gridApi.setGridOption("loading", true);
            cambiar_estado_select(true);

            const selectFechas = $('#actualizacion-select');
            const fecha = selectFechas.val();
            const selectCuerpo = $('#cuerpo-select');
            const selectEspecialidad = $('#especialidad-select');

            $('#cuerposSpinner').removeClass('d-none');
            $('#especialidadesSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/cuerpos?fecha=${fecha}&format=json`)
            .then(response => response.json())
            .then(data => {
                selectCuerpo.empty();

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.codigo,
                        text: `${item.nombre} (0${item.codigo})`
                    });
                    selectCuerpo.append(option);
                });

                $('#cuerposSpinner').addClass('d-none');

                return fetch(`${API_BASE_URL}api/especialidades?fecha=${fecha}&cuerpo=${selectCuerpo.val()}&format=json`);
            })
            .then(response => response.json())
            .then(data => {
                selectEspecialidad.empty();

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.id,
                        text: `${item.nombre} (${item.codigo})`
                    });
                    selectEspecialidad.append(option);
                });

                $('#especialidadesSpinner').addClass('d-none');

                return fetch(`${API_BASE_URL}api/registro-interinos/?fecha=${fecha}&especialidad=${selectEspecialidad.val()}&format=json`);
            })
            .then(response => response.json())
            .then(data => {
                gridApi.setGridOption("rowData", data);
                gridApi.autoSizeColumns(['orden', 'idiomas']);
            })
            .catch(error => {
                console.error("Hubo un problema con la petición Fetch:", error.message);
            })
            .finally(() => {
                gridApi.setGridOption("loading", false);
                cambiar_estado_select(false);
            });
        });

        $('#cuerpo-select').on('change', function () {
            gridApi.setGridOption("loading", true);
            cambiar_estado_select(true);

            const selectFechas = $('#actualizacion-select');

            $('#especialidadesSpinner').removeClass('d-none');

            fetch(`${API_BASE_URL}api/especialidades?fecha=${selectFechas.val()}&cuerpo=${$(this).val()}&format=json`)
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

                return fetch(`${API_BASE_URL}api/registro-interinos/?fecha=${selectFechas.val()}&especialidad=${selectEspecialidad.val()}&format=json`);
            })
            .then(res => res.json())
            .then((data) => {
                    gridApi.setGridOption("rowData", data);
                    gridApi.autoSizeColumns(['orden', 'idiomas']);
            })
            .catch(err => {
                console.error("Error en la carga de datos:", err);
            })
            .finally(() => {
                gridApi.setGridOption("loading", false);
                cambiar_estado_select(false);
            });
        });

        $('#especialidad-select').on('change', function () {
            gridApi.setGridOption("loading", true);
            cambiar_estado_select(true);

            const selectFechas = $('#actualizacion-select');

            fetch(`${API_BASE_URL}api/registro-interinos/?fecha=${selectFechas.val()}&especialidad=${$(this).val()}&format=json`)
            .then(response => response.json())
            .then((data) => {
                gridApi.setGridOption("rowData", data);
                gridApi.autoSizeColumns(['orden', 'idiomas']);
            })
            .finally(() => {
                gridApi.setGridOption("loading", false);
                cambiar_estado_select(false);
            });
        });
    });
}


function cambiar_estado_select(disabled) {
    $('#actualizacion-select').prop('disabled', disabled);
    $('#cuerpo-select').prop('disabled', disabled);
    $('#especialidad-select').prop('disabled', disabled);
}


function create_aggrid_table() {
    const myTheme = agGrid.themeQuartz.withParams({
      // headerBackgroundColor: "#007BFF1F",
      headerVerticalPaddingScale: 0.8,
      rowVerticalPaddingScale: 0.8
    });

    const gridOptions = {
        theme: myTheme,
        pagination: false,
        localeText: AG_GRID_LOCALE_ES,
        suppressDragLeaveHidesColumns: true,
        defaultColDef: {
            filter: false,
            suppressMovable: true,
        },
        columnDefs: [
            {
                headerName: "Fecha",
                field: "fecha",
                hide: true,
                suppressColumnsToolPanel: true
            },
            {
                headerName: '#',
                colId: "orden",
                valueGetter: (params) => {
                    if (params.data && params.data.orden == null) {
                        return '';
                    }

                    let count = 0;
                    let result = '';

                    params.api.forEachNodeAfterFilterAndSort((node) => {
                        if (node.data && node.data.orden != null) {
                            count++;
                            if (node === params.node) {
                                result = count;
                            }
                        }
                    });

                    return result;
                },
                resizable: false,
                headerStyle: { paddingLeft: '10px', paddingRight: '0px' },
                cellStyle: { paddingLeft: '10px', paddingRight: '0px' }
            },
            {
                headerName: '',
                colId: "idiomas",
                cellRenderer: (params) => {
                    const idiomas = {
                      italiano: 'it',
                      ingles: 'gb',
                      aleman: 'de',
                      frances: 'fr'
                    };

                    const flagsHtml = Object.entries(idiomas)
                        .filter(([idioma]) => params.data[idioma])
                        .map(([idioma, codigoBandera]) => {
                            return `<img
                                src="https://flagcdn.com/20x15/${codigoBandera}.png"
                                srcset="https://flagcdn.com/40x30/${codigoBandera}.png 2x, https://flagcdn.com/60x45/${codigoBandera}.png 3x"
                                alt="${idioma}"
                                width="20px"
                                height="15px"
                                </img>`;
                      })
                      .join(' ');

                    return flagsHtml;
                },
                headerStyle: { paddingLeft: '0px', paddingRight: '0px' },
                cellStyle: { paddingLeft: '0px', paddingRight: '0px' }
            },
            {
                headerName: "Nombre",
                field: "nombre",
                minWidth: 85,
                width: 120,
                headerStyle: { paddingLeft: '5px', paddingRight: '5px' },
                cellStyle: { paddingLeft: '0px', paddingRight: '0px' }
            },
            {
                headerName: "Apellidos",
                field: "apellidos",
                minWidth: 95,
                width: 190,
                headerStyle: { paddingLeft: '5px', paddingRight: '5px' },
                cellStyle: { paddingLeft: '0px', paddingRight: '0px' }
            },
            {
                headerName: "DNI",
                field: "dni",
                minWidth: 60,
                width: 100,
            },
            {
                headerName: "Pos. Bolsa General",
                field: "orden_bolsa",
            }
        ],
        onGridReady: (params) => {
            cambiar_estado_select(true);

            const body = document.body;
            const param_fecha = body.dataset.fecha;
            const param_cuerpo = body.dataset.cuerpo;
            const param_especialidad = body.dataset.especialidad;

            const selectFechas = $('#actualizacion-select');
            const selectCuerpos = $('#cuerpo-select');
            const selectEspecialidad = $('#especialidad-select');

            fetch(`${API_BASE_URL}api/fechas-registros?format=json`)
            .then(response => response.json())
            .then((data) => {

                selectFechas.empty();
                $('#fechasSpinner').addClass('d-none');

                data.forEach(item => {
                    const [dia, mes, anio] = item.fecha.split("/");

                    const option = $('<option>', {
                        value: `${anio}-${mes}-${dia}`,
                        text: `${item.fecha}`
                    });
                    selectFechas.append(option);
                });

                if (param_fecha) {
                    selectFechas.val(param_fecha);
                }

                return fetch(`${API_BASE_URL}api/cuerpos?fecha=${selectFechas.val()}&format=json`);
            })
            .then(res => res.json())
            .then((data) => {
                selectCuerpos.empty();
                $('#cuerposSpinner').addClass('d-none');

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.codigo,
                        text: `${item.nombre} (0${item.codigo})`
                    });
                    selectCuerpos.append(option);
                });

                if (param_cuerpo) {
                    selectCuerpos.val(param_cuerpo);
                }

                return fetch(`${API_BASE_URL}api/especialidades?fecha=${selectFechas.val()}&cuerpo=${selectCuerpos.val()}&format=json`);
            })
            .then(res => res.json())
            .then((data) => {
                selectEspecialidad.empty();
                $('#especialidadesSpinner').addClass('d-none');

                data.forEach(item => {
                    const option = $('<option>', {
                        value: item.id,
                        text: `${item.nombre} (${item.codigo})`
                    });
                    selectEspecialidad.append(option);
                });

                if (param_especialidad) {
                    selectEspecialidad.val(param_especialidad);
                }

                return fetch(`${API_BASE_URL}api/registro-interinos/?fecha=${selectFechas.val()}&especialidad=${selectEspecialidad.val()}&format=json`);
            })
            .then(response => response.json())
            .then((data) => {
                params.api.setGridOption("rowData", data);
                params.api.autoSizeColumns(['orden', 'idiomas']);
            })
            .catch(error => {
                console.error("Hubo un problema con la petición Fetch:", error.message);
            })
            .finally(() => {
                cambiar_estado_select(false);
            });

            /*
            if (window.innerWidth < 576) {
                params.api.setColumnsVisible(["dni", "orden_bolsa"], false);
            } else {
                // params.api.setColumnsVisible(["DNI"], false);
            };
            */
        },
        onCellClicked: (event) => {
            const params = new URLSearchParams({
                nombre: event.data.nombre,
                apellidos: event.data.apellidos,
                dni: event.data.dni,
                cuerpo: event.data.especialidad.cuerpo.codigo,
                especialidad: event.data.especialidad.id,
                fecha: event.data.fecha
            });

            window.location.href = `/detalle-interino?${params.toString()}`;
        },
        onFirstDataRendered: (params) => {
        },
        rowClassRules: {
            'fila-adjudicado': (params) => params.data && params.data.orden == null
        }
    };

    return agGrid.createGrid(document.querySelector("#myGrid"), gridOptions);
}

init();