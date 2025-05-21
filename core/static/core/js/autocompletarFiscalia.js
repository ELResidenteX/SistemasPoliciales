document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('inputFiscalia');
  const sugerencias = document.getElementById('sugerencias');

  if (!input || !sugerencias) return;

  let fiscalias = [];

  // Cargar fiscalías desde JSON precargado y almacenar en la variable
  fetch('/static/core/json/fiscalias_nombres.json')
    .then(res => res.json())
    .then(data => {
      fiscalias = data; // ✅ guardar en variable global fiscalias
    });

  input.addEventListener('input', function () {
    const query = input.value.toLowerCase();
    sugerencias.innerHTML = '';

    if (query.length === 0) return;

    const filtradas = fiscalias.filter(f => f.toLowerCase().includes(query)).slice(0, 5);

    filtradas.forEach(nombre => {
      const item = document.createElement('button');
      item.className = 'list-group-item list-group-item-action';
      item.textContent = nombre;
      item.type = 'button';
      item.onclick = () => {
        input.value = nombre;
        sugerencias.innerHTML = '';
      };
      sugerencias.appendChild(item);
    });
  });

  document.addEventListener('click', function (e) {
    if (!sugerencias.contains(e.target) && e.target !== input) {
      sugerencias.innerHTML = '';
    }
  });
});

