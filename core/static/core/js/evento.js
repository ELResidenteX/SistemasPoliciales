// Script para cargar dinámicamente Región, Provincia y Comuna en el formulario de EVENTO

document.addEventListener("DOMContentLoaded", function () {
  const regionSelect = document.getElementById("region");
  const provinciaSelect = document.getElementById("provincia");
  const comunaSelect = document.getElementById("comuna");

  const selectedRegion = regionSelect?.getAttribute("data-selected");
  const selectedProvincia = provinciaSelect?.getAttribute("data-selected");
  const selectedComuna = comunaSelect?.getAttribute("data-selected");

  if (regionSelect && provinciaSelect && comunaSelect) {
    fetch("/static/core/json/regiones_chile.json")
      .then((response) => response.json())
      .then((data) => {
        // Cargar regiones
        data.forEach((region) => {
          const option = document.createElement("option");
          option.value = region.region;
          option.textContent = region.region;
          if (region.region === selectedRegion) {
            option.selected = true;
          }
          regionSelect.appendChild(option);
        });

        // Si ya hay una región seleccionada, cargar provincias
        if (selectedRegion) {
          const regionObj = data.find((r) => r.region === selectedRegion);
          if (regionObj) {
            provinciaSelect.innerHTML = '<option value="">Seleccione provincia</option>';
            regionObj.provincias.forEach((prov) => {
              const option = document.createElement("option");
              option.value = prov.name;
              option.textContent = prov.name;
              if (prov.name === selectedProvincia) {
                option.selected = true;
              }
              provinciaSelect.appendChild(option);
            });
            provinciaSelect.disabled = false;

            // Si ya hay una provincia seleccionada, cargar comunas
            if (selectedProvincia) {
              const provObj = regionObj.provincias.find((p) => p.name === selectedProvincia);
              if (provObj) {
                comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
                provObj.comunas.forEach((com) => {
                  const option = document.createElement("option");
                  option.value = com.name;
                  option.textContent = com.name;
                  if (com.name === selectedComuna) {
                    option.selected = true;
                  }
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

          const selectedRegionObj = data.find((r) => r.region === this.value);
          if (selectedRegionObj) {
            selectedRegionObj.provincias.forEach((prov) => {
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

          const selectedRegionObj = data.find((r) => r.region === regionSelect.value);
          const selectedProvObj = selectedRegionObj?.provincias.find((p) => p.name === this.value);
          if (selectedProvObj) {
            selectedProvObj.comunas.forEach((com) => {
              const option = document.createElement("option");
              option.value = com.name;
              option.textContent = com.name;
              comunaSelect.appendChild(option);
            });
            comunaSelect.disabled = false;
          }
        });
      })
      .catch((error) => console.error("Error cargando regiones:", error));
  }
});


//RETROCEDER UNA
  