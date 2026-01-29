// Initialiser la carte
// Check if map is already initialized to avoid error on re-include or htmx swap if applicable, 
// though here it's full page load mostly.
// However, L.map('map') throws if container already has map.

var container = L.DomUtil.get('map');
if(container != null){
    container._leaflet_id = null;
}

var map = L.map('map').setView([46.8, 2.4], 6); // Centre sur la France

// Ajouter le fond de carte OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var markersLayer = L.layerGroup().addTo(map);

// On définit la fonction globalement pour qu'elle soit appelable par hx-on
window.refreshMap = function() {
    // 1. Effacer les anciens markers
    markersLayer.clearLayers();

    // 🔥 IMPORTANT : forcer Leaflet à recalculer la taille
    map.invalidateSize();
    
    // 2. Parcourir les nouveaux éléments injectés par HTMX
    var bounds = L.latLngBounds();
    var hasMarkers = false;

    const data = JSON.parse(document.getElementById('geo-data').textContent);
    if (data?.center) {
        const marker = L.marker(data.center.position);
        markersLayer.addLayer(marker);
        bounds.extend(data.center.position);
        hasMarkers = true;
    }

    if (data?.points) {
        data?.points.forEach(point => {
            const marker = L.marker(point.position);
            marker.bindPopup(point.title);
            markersLayer.addLayer(marker);
            bounds.extend(point.position);
            hasMarkers = true;
        })
    }

    // 3. Optionnel : Recadrer la carte pour voir tous les nouveaux points
    if (hasMarkers) {
        map.fitBounds(bounds.pad(0.1));
    }
};

function onMapTabShown() {
    // 🔥 IMPORTANT : forcer Leaflet à recalculer la taille
    map.invalidateSize();

    refreshMap();
}