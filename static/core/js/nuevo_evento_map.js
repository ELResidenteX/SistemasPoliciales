// Inicializa autocomplete y mini-map para nuevo_evento
let map, marker, autocomplete;

function initAutocompleteAndMap() {
  const input = document.getElementById("id_direccion");
  if (!input || !window.google || !window.google.maps || !window.google.maps.places) return;
  autocomplete = new google.maps.places.Autocomplete(input, {
    types: ["geocode"],
    componentRestrictions: { country: "cl" }
  });

  map = new google.maps.Map(document.getElementById("mini-map"), {
    center: { lat: -33.45, lng: -70.66 },
    zoom: 14,
  });

  marker = new google.maps.Marker({ map: map, draggable: false });

  autocomplete.addListener("place_changed", function () {
    const place = autocomplete.getPlace();
    if (!place || !place.geometry) return;
    map.setCenter(place.geometry.location);
    marker.setPosition(place.geometry.location);
  });
}

document.addEventListener('DOMContentLoaded', function () {
  // Si la API de Google ya está cargada, inicializamos; si no, la inicializaremos cuando cargue.
  if (window.google && google.maps && google.maps.places) initAutocompleteAndMap();
  // Si la API se carga después, la plantilla incluye la llamada a la inicialización por su cuenta (por seguridad).
});

export { initAutocompleteAndMap };
