// core/js/modalParte.js

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const abrirModal = urlParams.get("abrir_modal");
    const eventoId = urlParams.get("evento_id");
  
    if (abrirModal === "1" && eventoId) {
      const modalElement = document.getElementById(`modalGenerarParte${eventoId}`);
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      }
    }
  });
  