document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("juzgado-select");
  const btnGenerar = document.getElementById("btn-generar-parte");

  if (!select) return;

  fetch("/static/infracciones/json/juzpol.json")
    .then(response => response.json())
    .then(data => {
      for (const region in data) {
        data[region].forEach(juzgado => {
          const option = document.createElement("option");
          option.value = juzgado.nombre;  // Esto se enviará al backend
          option.textContent = `${juzgado.nombre} (${juzgado.comuna})`;
          select.appendChild(option);
        });
      }
    });

  select.addEventListener("change", function () {
    if (btnGenerar) {
      btnGenerar.disabled = !select.value;
    }
  });
});

  