// Global map instance and markers array
let leafletMap;
let trainLocationMarkers = [];

// Sample station coordinates - You'll want to expand this with more stations
// Get comprehensive data from MTA's GTFS static feed (stops.txt)
const STATION_COORDINATES_DATA = {
    // Times Square area
    'A27': { lat: 40.755417, lng: -73.986664, name: 'Times Sq-42 St (A,C,E)' },
    'R16': { lat: 40.755417, lng: -73.986664, name: 'Times Sq-42 St (N,Q,R,W)' },
    '127': { lat: 40.755417, lng: -73.986664, name: 'Times Sq-42 St (1,2,3)' },
    '901': { lat: 40.755417, lng: -73.986664, name: 'Times Sq-42 St (7)' },
    '725': { lat: 40.755417, lng: -73.986664, name: 'Times Sq-42 St (S)' },
    
    // Grand Central
    '631': { lat: 40.752769, lng: -73.979187, name: 'Grand Central-42 St' },
    
    // Union Square
    'R20': { lat: 40.735736, lng: -73.990568, name: '14 St-Union Sq (N,Q,R,W)' },
    'L08': { lat: 40.735736, lng: -73.990568, name: '14 St-Union Sq (L)' },
    '635': { lat: 40.735736, lng: -73.990568, name: '14 St-Union Sq (4,5,6)' },
    
    // Herald Square
    'D17': { lat: 40.749719, lng: -73.987823, name: '34 St-Herald Sq (B,D,F,M)' },
    'R17': { lat: 40.749719, lng: -73.987823, name: '34 St-Herald Sq (N,Q,R,W)' },
    
    // Wall Street area
    'R27': { lat: 40.706821, lng: -74.008834, name: 'Whitehall St-South Ferry (R,W)' },
    'R25': { lat: 40.704817, lng: -74.013408, name: 'Rector St (R,W)' },
    
    // Brooklyn Bridge
    'R29': { lat: 40.708359, lng: -74.003967, name: 'Bowling Green (R,W)' },
    '142': { lat: 40.713065, lng: -73.996379, name: 'Fulton St (4,5,6)' },
    
    // More stations - you can add many more from the GTFS data
    'D21': { lat: 40.730019, lng: -73.991013, name: 'W 4 St-Washington Sq' },
    'A32': { lat: 40.720595, lng: -74.007107, name: 'Chambers St (A,C)' },
    'R30': { lat: 40.720595, lng: -74.007107, name: 'Chambers St (R,W)' }
};

function initLeafletMap(mapId) {
    // Create map centered on NYC
    leafletMap = L.map(mapId).setView([40.7589, -73.9851], 12);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        minZoom: 10
    }).addTo(leafletMap);
    
    return leafletMap;
}

// Update map with train locations
window.updateMapWithTrainLocations = function(allTrainData, getLineColorFunc) {
    if (!leafletMap) return;

    // Clear existing markers
    trainLocationMarkers.forEach(marker => leafletMap.removeLayer(marker));
    trainLocationMarkers = [];
    
    // Group trains by station for better visualization
    const trainsByStation = {};
    
    allTrainData.forEach(train => {
        // Try to find station coordinates
        const parentStationId = train.stopId.length > 1 ? train.stopId.slice(0, -1) : train.stopId;
        const stationGenericId = train.stopId.substring(0, 3);

        let stationInfo = STATION_COORDINATES_DATA[train.stopId] || 
                         STATION_COORDINATES_DATA[parentStationId] || 
                         STATION_COORDINATES_DATA[stationGenericId];
        
        if (stationInfo) {
            const key = `${stationInfo.lat},${stationInfo.lng}`;
            if (!trainsByStation[key]) {
                trainsByStation[key] = {
                    station: stationInfo,
                    trains: []
                };
            }
            trainsByStation[key].trains.push(train);
        }
    });
    
    // Create markers for each station with trains
    Object.values(trainsByStation).forEach(({ station, trains }) => {
        const routes = [...new Set(trains.map(t => t.routeId))].sort();
        const primaryRoute = routes[0];
        
        const marker = L.circleMarker([station.lat, station.lng], {
            radius: Math.min(8 + routes.length * 2, 15),
            fillColor: getLineColorFunc(primaryRoute) || '#555555',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Create popup content
        const routeList = routes.map(route => 
            `<span style="background-color: ${getLineColorFunc(route)}; color: ${route.match(/[NQRWnqrw]/) ? 'black' : 'white'}; padding: 2px 6px; border-radius: 3px; margin: 1px; display: inline-block; font-weight: bold;">${route}</span>`
        ).join(' ');
        
        const popupContent = `
            <div>
                <strong>${station.name}</strong><br>
                <div style="margin: 5px 0;">${routeList}</div>
                <small>${trains.length} train update(s)</small>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        marker.addTo(leafletMap);
        trainLocationMarkers.push(marker);
    });
    
    console.log(`Mapped ${Object.keys(trainsByStation).length} stations with ${allTrainData.length} train updates`);
};