document.addEventListener("DOMContentLoaded", function () {
    // Cargar JSON una vez
    fetch("/static/core/json/regiones_chile.json")
      .then(response => response.json())
      .then(data => {
        const regionesData = data;
  
        // Inicializar selects para evento y participantes
        document.querySelectorAll(".region-select").forEach(regionSelect => {
          const tipo = regionSelect.dataset.tipo;
          const id = regionSelect.dataset.id;
  
          const provinciaSelect = document.querySelector(`.provincia-select[data-tipo="${tipo}"][data-id="${id}"]`);
          const comunaSelect = document.querySelector(`.comuna-select[data-tipo="${tipo}"][data-id="${id}"]`);
  
          const selectedRegion = regionSelect.getAttribute("data-selected");
          const selectedProvincia = provinciaSelect?.getAttribute("data-selected");
          const selectedComuna = comunaSelect?.getAttribute("data-selected");
  
          // Poblar regiones
          regionSelect.innerHTML = '<option value="">Seleccione Región</option>';
          regionesData.forEach(region => {
            const option = document.createElement('option');
            option.value = region.region;
            option.textContent = region.region;
            if (region.region === selectedRegion) option.selected = true;
            regionSelect.appendChild(option);
          });
  
          // Si ya hay región seleccionada, poblar provincias y comunas
          if (selectedRegion) {
            const regObj = regionesData.find(r => r.region === selectedRegion);
            if (regObj && provinciaSelect) {
              provinciaSelect.innerHTML = '<option value="">Seleccione Provincia</option>';
              regObj.provincias.forEach(prov => {
                const option = document.createElement("option");
                option.value = prov.name;
                option.textContent = prov.name;
                if (prov.name === selectedProvincia) option.selected = true;
                provinciaSelect.appendChild(option);
  
                // Si provincia coincide, poblar comunas
                if (prov.name === selectedProvincia && comunaSelect) {
                  comunaSelect.innerHTML = '<option value="">Seleccione Comuna</option>';
                  prov.comunas.forEach(com => {
                    const opt = document.createElement("option");
                    opt.value = com.name;
                    opt.textContent = com.name;
                    if (com.name === selectedComuna) opt.selected = true;
                    comunaSelect.appendChild(opt);
                  });
                }
              });
            }
          }
  
          // Eventos de cambio
          regionSelect.addEventListener("change", function () {
            const selected = regionesData.find(r => r.region === this.value);
            provinciaSelect.innerHTML = '<option value="">Seleccione Provincia</option>';
            comunaSelect.innerHTML = '<option value="">Seleccione Comuna</option>';
            if (selected) {
              selected.provincias.forEach(prov => {
                const option = document.createElement("option");
                option.value = prov.name;
                option.textContent = prov.name;
                provinciaSelect.appendChild(option);
              });
            }
          });
  
          provinciaSelect.addEventListener("change", function () {
            const regionObj = regionesData.find(r => r.region === regionSelect.value);
            const provinciaObj = regionObj?.provincias.find(p => p.name === this.value);
            comunaSelect.innerHTML = '<option value="">Seleccione Comuna</option>';
            if (provinciaObj) {
              provinciaObj.comunas.forEach(com => {
                const option = document.createElement("option");
                option.value = com.name;
                option.textContent = com.name;
                comunaSelect.appendChild(option);
              });
            }
          });
        });
      })
      .catch(err => console.error("Error cargando regiones:", err));
  });
  