// Script general para funcionalidades comunes en la página
document.addEventListener('DOMContentLoaded', function () {
    // Ocultar alertas después de 5 segundos
    const alertBox = document.getElementById("eventoAlert");
    if (alertBox) {
      setTimeout(() => {
        alertBox.style.display = "none";
      }, 5000);
    }
  
    // Activar la pestaña correspondiente según parámetro en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab');
    
    if (activeTab === 'especie') {
      const especieTab = document.querySelector('#tab-especie');
      if (especieTab) {
        new bootstrap.Tab(especieTab).show();
      }
    } else if (activeTab === 'participante') {
      const participanteTab = document.querySelector('#tab-participante');
      if (participanteTab) {
        new bootstrap.Tab(participanteTab).show();
      }
    }
  });
  