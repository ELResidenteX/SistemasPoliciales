function imprimirParteById(containerId) {
  const contenidoEl = document.getElementById(containerId);
  if (!contenidoEl) return;
  const contenido = contenidoEl.innerHTML;
  const ventana = window.open('', '', 'height=800,width=800');
  ventana.document.write('<html><head><title>Imprimir Parte Policial</title>');
  ventana.document.write('</head><body>');
  ventana.document.write(contenido);
  ventana.document.write('</body></html>');
  ventana.document.close();
  ventana.focus();
  ventana.print();
  ventana.close();
}

window.imprimirParte = function () { imprimirParteById('vista-previa-parte'); };

document.addEventListener('DOMContentLoaded', function () {
  // Si hubiera botones con data-imprimir, los enlazamos
  document.querySelectorAll('[data-imprimir-target]').forEach(btn => {
    btn.addEventListener('click', function () {
      const target = this.getAttribute('data-imprimir-target') || 'vista-previa-parte';
      imprimirParteById(target);
    });
  });
});
