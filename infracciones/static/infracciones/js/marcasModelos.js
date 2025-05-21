document.addEventListener('DOMContentLoaded', function () {
  const tipoVehiculoSelect = document.getElementById('tipo_vehiculo');
  const marcaSelect = document.getElementById('marca');
  const modeloSelect = document.getElementById('modelo');

  let datosMarcas = [];

  // Cargar el JSON de marcas y modelos
  fetch('/static/infracciones/json/modeloautos.json')
    .then(response => response.json())
    .then(data => {
      datosMarcas = data.marcas;
      // Deshabilitar marca y modelo hasta que se seleccione el tipo de vehículo
      marcaSelect.disabled = true;
      modeloSelect.disabled = true;
    });

  // Evento al cambiar el tipo de vehículo
  tipoVehiculoSelect.addEventListener('change', function () {
    const tipoSeleccionado = this.value;
    // Limpiar y deshabilitar los selects
    marcaSelect.innerHTML = '<option value=\"\">Seleccione marca...</option>';
    modeloSelect.innerHTML = '<option value=\"\">Seleccione modelo...</option>';
    marcaSelect.disabled = true;
    modeloSelect.disabled = true;

    if (tipoSeleccionado) {
      // Filtrar marcas que tienen modelos del tipo seleccionado
      const marcasFiltradas = datosMarcas.filter(marca =>
        marca.modelos.some(modelo => modelo.tipo === tipoSeleccionado)
      );

      // Agregar las marcas al select
      marcasFiltradas.forEach(marca => {
        const option = document.createElement('option');
        option.value = marca.nombre;
        option.textContent = marca.nombre;
        marcaSelect.appendChild(option);
      });

      marcaSelect.disabled = false;
    }
  });

  // Evento al cambiar la marca
  marcaSelect.addEventListener('change', function () {
    const marcaSeleccionada = this.value;
    const tipoSeleccionado = tipoVehiculoSelect.value;
    modeloSelect.innerHTML = '<option value=\"\">Seleccione modelo...</option>';
    modeloSelect.disabled = true;

    if (marcaSeleccionada) {
      // Buscar la marca seleccionada
      const marca = datosMarcas.find(m => m.nombre === marcaSeleccionada);
      if (marca) {
        // Filtrar modelos por tipo de vehículo
        const modelosFiltrados = marca.modelos.filter(modelo => modelo.tipo === tipoSeleccionado);
        // Agregar los modelos al select
        modelosFiltrados.forEach(modelo => {
          const option = document.createElement('option');
          option.value = modelo.nombre;
          option.textContent = modelo.nombre;
          modeloSelect.appendChild(option);
        });
        modeloSelect.disabled = false;
      }
    }
  });
});
