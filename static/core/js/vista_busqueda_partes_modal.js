document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[id^="modalParte"]').forEach(modal => {
    modal.addEventListener('show.bs.modal', function () {
      const parteId = this.id.replace("modalParte", "");
      fetch(`/parte/${parteId}/vista-previa-modal/`)
        .then(response => response.text())
        .then(html => {
          const target = document.getElementById("modalParteContent" + parteId);
          if (target) target.innerHTML = html;
        });
    });
  });
});
