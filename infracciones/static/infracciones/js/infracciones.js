document.addEventListener("DOMContentLoaded", function () {
  // Región - Provincia - Comuna
  const regionSelect = document.getElementById("region-select");
  const provinciaSelect = document.getElementById("provincia-select");
  const comunaSelect = document.getElementById("comuna-select");

  fetch("/static/core/json/regiones_chile.json")
    .then(response => response.json())
    .then(data => {
      // Cargar regiones
      data.forEach(region => {
        const option = document.createElement("option");
        option.value = region.region;
        option.textContent = region.region;
        regionSelect.appendChild(option);
      });

      regionSelect.addEventListener("change", function () {
        const regionSeleccionada = this.value;
        provinciaSelect.innerHTML = '<option value="">Seleccione una provincia...</option>';
        comunaSelect.innerHTML = '<option value="">Seleccione una comuna...</option>';

        const region = data.find(r => r.region === regionSeleccionada);
        if (region) {
          region.provincias.forEach(prov => {
            const option = document.createElement("option");
            option.value = prov.name;
            option.textContent = prov.name;
            provinciaSelect.appendChild(option);
          });
        }
      });

      provinciaSelect.addEventListener("change", function () {
        const regionSeleccionada = regionSelect.value;
        const provinciaSeleccionada = this.value;
        comunaSelect.innerHTML = '<option value="">Seleccione una comuna...</option>';

        const region = data.find(r => r.region === regionSeleccionada);
        const provincia = region?.provincias.find(p => p.name === provinciaSeleccionada);
        if (provincia) {
          provincia.comunas.forEach(com => {
            const option = document.createElement("option");
            option.value = com.name;
            option.textContent = com.name;
            comunaSelect.appendChild(option);
          });
        }
      });
    })
    .catch(error => {
      console.error("Error cargando regiones:", error);
    });

  // -------------------------
  // Cargar tipos de infracción
  let infraccionesData = [];

  fetch("/static/infracciones/json/infracciones_transito.json")
    .then(response => response.json())
    .then(data => {
      infraccionesData = data.infracciones;

      // Llenar el primer select (ya renderizado)
      const primerosSelects = document.querySelectorAll(".tipo-infraccion-select");
      primerosSelects.forEach(select => llenarOpcionesInfraccion(select));
    })
    .catch(error => {
      console.error("Error cargando tipos de infracción:", error);
    });

  // Función para llenar un select con infracciones
  function llenarOpcionesInfraccion(selectElement) {
    selectElement.innerHTML = '<option value="">Seleccione una infracción...</option>';
    infraccionesData.forEach(item => {
      const option = document.createElement("option");
      option.value = item.descripcion;
      option.textContent = item.descripcion;
      selectElement.appendChild(option);
    });
  }

  // -------------------------
  // Agregar más selects de infracción dinámicamente
  window.agregarCampoInfraccion = function () {
    const contenedor = document.getElementById("contenedor-infracciones");
    const div = document.createElement("div");
    div.classList.add("d-flex", "mb-2");

    const select = document.createElement("select");
    select.name = "tipos_infraccion[]";
    select.className = "form-select me-2 tipo-infraccion-select";
    select.required = true;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-danger";
    btn.innerHTML = "🗑️";
    btn.onclick = function () {
      contenedor.removeChild(div);
    };

    div.appendChild(select);
    div.appendChild(btn);
    contenedor.appendChild(div);

    // Llenar el nuevo select
    llenarOpcionesInfraccion(select);
  };
});
