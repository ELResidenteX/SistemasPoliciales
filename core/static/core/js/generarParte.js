document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const abrirModal = urlParams.get("abrir_modal");
    const eventoId = urlParams.get("evento_id");
  
    if (abrirModal === "1" && eventoId) {
      const modalId = `modalGenerarParte${eventoId}`;
      const modalElement = document.getElementById(modalId);
  
      if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
      }
    }
  });
  