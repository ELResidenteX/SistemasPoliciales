document.addEventListener("DOMContentLoaded", function () {
  const selectFiscalia = document.getElementById("fiscalia-select");

  if (selectFiscalia) {
    fetch("/static/core/json/fiscalias.json")
      .then(response => response.json())
      .then(data => {
        data.Regiones.forEach(region => {
          region.Fiscalias.forEach(fiscalia => {
            // Verificamos si la fiscalía tiene campo "Nombre"
            if (fiscalia.Nombre) {
              const option = document.createElement("option");
              option.value = fiscalia.Nombre;
              option.textContent = fiscalia.Nombre + " (" + region.Nombre + ")";
              selectFiscalia.appendChild(option);
            }
          });
        });
      })
      .catch(error => {
        console.error("Error cargando fiscalías:", error);
      });
  }
});
