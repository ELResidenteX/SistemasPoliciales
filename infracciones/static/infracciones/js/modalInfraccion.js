// Mostrar el modal si se indica desde la URL con ?mostrar_modal=1
document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const debeMostrar = params.get("mostrar_modal");
  
    const modalElement = document.getElementById("modalInfraccionCompleta");
    if (modalElement && debeMostrar === "1") {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    }
  });
  
  // Función para cerrar manualmente el modal (si lo necesitas)
  function cerrarModal() {
    const modalElement = document.getElementById("modalInfraccionCompleta");
    if (modalElement) {
      const modal = bootstrap.Modal.getInstance(modalElement);
      modal.hide();
    }
  }

  //generar parte

  document.addEventListener("DOMContentLoaded", function () {
    const mostrar = document.getElementById("modalInfraccionCompleta");
    if (mostrar && mostrar.dataset.mostrar === "true") {
      const modal = new bootstrap.Modal(mostrar);
      modal.show();
    }
  
    const btnGenerar = document.getElementById("btn-generar-parte");
    if (btnGenerar) {
      btnGenerar.addEventListener("click", function () {
        const select = document.getElementById("juzgado-select");
        const juzgado = select.value;
        const infraccionId = window.location.search.match(/infraccion_id=(\d+)/)?.[1];
  
        if (!juzgado || !infraccionId) return;
        console.log("ID infracción:", infraccionId);
console.log("Juzgado seleccionado:", juzgado);

  
        fetch(`/infracciones/parte/generar/${infraccionId}/`, {


          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
          },
          body: new URLSearchParams({ juzgado: juzgado })
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              window.location.href = data.redirect_url;
            } else {
              alert(data.error || "Ocurrió un error");
            }
          });
      });
    }
  
    function getCSRFToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
  });
  
  
  