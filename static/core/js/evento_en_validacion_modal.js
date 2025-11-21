document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[id^="modalVistaPrevia"]').forEach(modal => {
    modal.addEventListener('show.bs.modal', function () {
      const eventoId = this.id.replace("modalVistaPrevia", "");
      fetch(`/evento/${eventoId}/vista-previa/`)
        .then(response => response.text())
        .then(html => {
          const target = document.getElementById("modalVistaPreviaContent" + eventoId);
          if (target) target.innerHTML = html;
        });
    });
  });
});

function mostrarToastAcceso() {
  const toastEl = document.getElementById('toastAccesoRestringido');
  if (!toastEl || !window.bootstrap) return;
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}

window.mostrarToastAcceso = mostrarToastAcceso;
