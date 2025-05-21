function cargarVistaPrevia(eventoId) {
    fetch(`/evento/${eventoId}/vista-previa/`)
      .then(response => response.text())
      .then(html => {
        document.getElementById('modalContenidoVistaPrevia').innerHTML = html;
      })
      .catch(error => {
        console.error('Error al cargar vista previa:', error);
        document.getElementById('modalContenidoVistaPrevia').innerHTML = '<p>Error al cargar el contenido.</p>';
      });
  }
  

