document.addEventListener('DOMContentLoaded', function () {
  const checkboxEmpadronado = document.getElementById('empadronado');
  const camposInfractor = document.getElementById('campos-infractor');
  if (!checkboxEmpadronado || !camposInfractor) return;

  function toggleCampos() {
    if (checkboxEmpadronado.checked) {
      camposInfractor.style.display = 'none';
      camposInfractor.querySelectorAll('input, select').forEach(el => el.required = false);
    } else {
      camposInfractor.style.display = 'block';
      camposInfractor.querySelectorAll('input, select').forEach(el => el.required = true);
    }
  }

  checkboxEmpadronado.addEventListener('change', toggleCampos);
  toggleCampos();
});
