document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('juzgado-select');
    const boton = document.getElementById('btn-generar-parte');
    const respuesta = document.getElementById('respuesta-generar-parte');
  
    if (select && boton) {
      select.addEventListener('change', () => {
        boton.disabled = !select.value;
      });
  
      boton.addEventListener('click', () => {
        const juzgado = select.value;
        const infraccionId = boton.dataset.infraccionId;
  
        fetch(`/infracciones/generar_parte/${infraccionId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': window.csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `juzgado=${encodeURIComponent(juzgado)}`
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            respuesta.textContent = '✅ Parte generado correctamente.';
            respuesta.style.display = 'block';
            respuesta.classList.remove('text-danger');
            respuesta.classList.add('text-success');
  
            select.disabled = true;
            boton.disabled = true;
          } else {
            respuesta.textContent = data.error || '❌ Error al generar parte.';
            respuesta.style.display = 'block';
            respuesta.classList.remove('text-success');
            respuesta.classList.add('text-danger');
          }
        })
        .catch(() => {
          respuesta.textContent = '❌ Error en la solicitud.';
          respuesta.style.display = 'block';
          respuesta.classList.remove('text-success');
          respuesta.classList.add('text-danger');
        });
      });
    }
  });
  
  