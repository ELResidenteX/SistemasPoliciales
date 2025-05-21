// core/js/participantes.js

document.addEventListener("DOMContentLoaded", function () {
  fetch("/static/core/json/regiones_chile.json")
    .then(response => response.json())
    .then(regionesData => {
      document.querySelectorAll(".region-select").forEach(regionSelect => {
        const tipo = regionSelect.dataset.tipo;
        const id = regionSelect.dataset.id;

        const provinciaSelect = document.querySelector(`.provincia-select[data-tipo="${tipo}"][data-id="${id}"]`);
        const comunaSelect = document.querySelector(`.comuna-select[data-tipo="${tipo}"][data-id="${id}"]`);

        const selectedRegion = regionSelect.getAttribute("data-selected");
        const selectedProvincia = provinciaSelect?.getAttribute("data-selected");
        const selectedComuna = comunaSelect?.getAttribute("data-selected");

        // Limpiar y cargar regiones
        regionSelect.innerHTML = '<option value="">Seleccione región</option>';
        regionesData.forEach(region => {
          const option = document.createElement("option");
          option.value = region.region;
          option.textContent = region.region;
          if (region.region === selectedRegion) option.selected = true;
          regionSelect.appendChild(option);
        });

        // Si ya hay región seleccionada, cargar provincias
        if (selectedRegion) {
          const regionObj = regionesData.find(r => r.region === selectedRegion);
          if (regionObj) {
            provinciaSelect.innerHTML = '<option value="">Seleccione provincia</option>';
            regionObj.provincias.forEach(prov => {
              const option = document.createElement("option");
              option.value = prov.name;
              option.textContent = prov.name;
              if (prov.name === selectedProvincia) option.selected = true;
              provinciaSelect.appendChild(option);
            });
            provinciaSelect.disabled = false;

            // Si ya hay provincia seleccionada, cargar comunas
            if (selectedProvincia) {
              const provinciaObj = regionObj.provincias.find(p => p.name === selectedProvincia);
              if (provinciaObj) {
                comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
                provinciaObj.comunas.forEach(com => {
                  const option = document.createElement("option");
                  option.value = com.name;
                  option.textContent = com.name;
                  if (com.name === selectedComuna) option.selected = true;
                  comunaSelect.appendChild(option);
                });
                comunaSelect.disabled = false;
              }
            }
          }
        }

        // Listener cambio de región
        regionSelect.addEventListener("change", function () {
          provinciaSelect.innerHTML = '<option value="">Seleccione provincia</option>';
          comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
          provinciaSelect.disabled = true;
          comunaSelect.disabled = true;

          const regionObj = regionesData.find(r => r.region === this.value);
          if (regionObj) {
            regionObj.provincias.forEach(prov => {
              const option = document.createElement("option");
              option.value = prov.name;
              option.textContent = prov.name;
              provinciaSelect.appendChild(option);
            });
            provinciaSelect.disabled = false;
          }
        });

        // Listener cambio de provincia
        provinciaSelect.addEventListener("change", function () {
          comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
          comunaSelect.disabled = true;

          const regionObj = regionesData.find(r => r.region === regionSelect.value);
          const provinciaObj = regionObj?.provincias.find(p => p.name === this.value);
          if (provinciaObj) {
            provinciaObj.comunas.forEach(com => {
              const option = document.createElement("option");
              option.value = com.name;
              option.textContent = com.name;
              comunaSelect.appendChild(option);
            });
            comunaSelect.disabled = false;
          }
        });
      });
    })
    .catch(err => console.error("Error cargando regiones:", err));
});




