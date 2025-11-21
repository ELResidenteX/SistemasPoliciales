document.addEventListener('DOMContentLoaded', function() {
  const modalId = window.MODAL_VISTA_PREVIA_PARTE_ID;
  const url = window.MODAL_VISTA_PREVIA_PARTE_URL;
  if (!modalId || !url) return;

  const modal = document.getElementById('modalVistaParte' + modalId);
  if (!modal) return;

  modal.addEventListener('show.bs.modal', function () {
    fetch(url)
      .then(response => response.text())
      .then(html => {
        const target = document.getElementById("modalVistaParteContent" + modalId);
        if (target) target.innerHTML = html;
      });
  });
});
