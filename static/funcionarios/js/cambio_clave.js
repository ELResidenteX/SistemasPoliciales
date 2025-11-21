// Oculta mensajes y valida requisitos de contraseña en tiempo real
setTimeout(function () {
  const alerts = document.querySelectorAll('.alert-success, .alert-danger, .alert-error');
  alerts.forEach(alert => { alert.style.display = 'none'; });
}, 3000);

document.addEventListener('DOMContentLoaded', function () {
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  if (!passwordInputs.length) return;
  passwordInputs.forEach(input => {
    input.addEventListener('input', function () {
      const value = this.value;
      const lengthRule = document.getElementById('rule-length');
      lengthRule.classList.toggle('text-success', value.length >= 8);
      lengthRule.classList.toggle('text-danger', value.length < 8);
      const numberRule = document.getElementById('rule-similar');
      const onlyNumbers = /^\d+$/.test(value);
      numberRule.classList.toggle('text-success', !onlyNumbers && value.length > 0);
      numberRule.classList.toggle('text-danger', onlyNumbers || value.length === 0);
      const uppercaseRule = document.getElementById('rule-uppercase');
      const hasUppercase = /[A-Z]/.test(value);
      uppercaseRule.classList.toggle('text-success', hasUppercase);
      uppercaseRule.classList.toggle('text-danger', !hasUppercase);
      const symbolRule = document.getElementById('rule-symbol');
      const hasSymbol = /[^A-Za-z0-9]/.test(value);
      symbolRule.classList.toggle('text-success', hasSymbol);
      symbolRule.classList.toggle('text-danger', !hasSymbol);
    });
  });
});
