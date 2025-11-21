document.addEventListener('DOMContentLoaded', function () {
  const fechaInput = document.getElementById('id_fecha_nacimiento');
  const edadInput = document.getElementById('id_edad');
  if (!fechaInput || !edadInput) return;

  fechaInput.addEventListener('change', function () {
    const fechaNac = new Date(this.value);
    if (!isNaN(fechaNac.getTime())) {
      const hoy = new Date();
      let edad = hoy.getFullYear() - fechaNac.getFullYear();
      const m = hoy.getMonth() - fechaNac.getMonth();
      if (m < 0 || (m === 0 && hoy.getDate() < fechaNac.getDate())) {
        edad--;
      }
      edadInput.value = edad;
    } else {
      edadInput.value = '';
    }
  });
});
