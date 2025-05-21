document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modalVistaParte");
  const modalBody = document.getElementById("contenidoModalParte");

  modal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const url = button.getAttribute("data-url");

    modalBody.innerHTML = `<iframe src="${url}" width="100%" height="600" frameborder="0"></iframe>`;
  });

  modal.addEventListener("hidden.bs.modal", function () {
    modalBody.innerHTML = ""; // Limpia al cerrar
  });
});
