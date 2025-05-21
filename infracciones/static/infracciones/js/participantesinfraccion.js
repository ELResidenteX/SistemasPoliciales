document.addEventListener('DOMContentLoaded', function () {
    // ==============================
    // Cascada Región → Provincia → Comuna
    // ==============================
    const regionSelect = document.getElementById('region_part');
    const provinciaSelect = document.getElementById('provincia_part');
    const comunaSelect = document.getElementById('comuna_part');

    if (regionSelect && provinciaSelect && comunaSelect) {
        fetch('/static/core/json/regiones_chile.json')
            .then(response => response.json())
            .then(data => {
                data.forEach(region => {
                    let option = document.createElement('option');
                    option.value = region.region;
                    option.textContent = region.region;
                    regionSelect.appendChild(option);
                });

                regionSelect.addEventListener('change', function () {
                    provinciaSelect.innerHTML = '<option value="">Seleccione provincia</option>';
                    comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
                    provinciaSelect.disabled = true;
                    comunaSelect.disabled = true;

                    const selectedRegion = data.find(r => r.region === this.value);
                    if (selectedRegion) {
                        selectedRegion.provincias.forEach(prov => {
                            let option = document.createElement('option');
                            option.value = prov.name;
                            option.textContent = prov.name;
                            provinciaSelect.appendChild(option);
                        });
                        provinciaSelect.disabled = false;
                    }
                });

                provinciaSelect.addEventListener('change', function () {
                    comunaSelect.innerHTML = '<option value="">Seleccione comuna</option>';
                    comunaSelect.disabled = true;

                    const selectedRegion = data.find(r => r.region === regionSelect.value);
                    const selectedProv = selectedRegion?.provincias.find(p => p.name === this.value);
                    if (selectedProv) {
                        selectedProv.comunas.forEach(com => {
                            let option = document.createElement('option');
                            option.value = com.name;
                            option.textContent = com.name;
                            comunaSelect.appendChild(option);
                        });
                        comunaSelect.disabled = false;
                    }
                });
            })
            .catch(error => console.error('Error cargando regiones:', error));
    }

    // ==============================
    // Lógica para ocultar campos si es empadronado
    // ==============================
    const empadronadoCheckbox = document.getElementById('empadronado');
    const infractorFields = document.querySelectorAll('.campo-infractor');

    if (empadronadoCheckbox) {
        function toggleInfractorFields() {
            const isChecked = empadronadoCheckbox.checked;
            infractorFields.forEach(field => {
                field.style.display = isChecked ? 'none' : 'block';
                const input = field.querySelector('input, select');
                if (input) {
                    input.required = !isChecked;
                }
            });
        }

        empadronadoCheckbox.addEventListener('change', toggleInfractorFields);
        toggleInfractorFields(); // Aplicar al cargar
    }
});
