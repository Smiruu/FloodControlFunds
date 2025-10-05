import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import useMapData from "../hooks/useMap"; // your custom hook

// Import marker icons (Vite compatible)
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const FloodMap = () => {
  const { data, loading, error } = useMapData();

  const riskColors = {
    Low: "green",
    Medium: "orange",
    High: "red",
  };

  return (
    <div className="w-full h-full border-2 border-gray-300 rounded-xl overflow-hidden flex flex-col">
      {/* Legend ABOVE the map */}
      <div className="bg-white p-2 border-b flex justify-around items-center">
        <strong>Legend:</strong>
        <div className="flex items-center">
          <span className="bg-green-500 w-4 h-4 rounded-full mr-2"></span>
          Low Risk
        </div>
        <div className="flex items-center">
          <span className="bg-orange-500 w-4 h-4 rounded-full mr-2"></span>
          Medium Risk
        </div>
        <div className="flex items-center">
          <span className="bg-red-500 w-4 h-4 rounded-full mr-2"></span>
          High Risk
        </div>
      </div>

      {/* Loading / Error States */}
      {loading && (
        <div className="flex-1 flex items-center justify-center bg-gray-50 text-gray-600">
          <p>Loading flood risk data...</p>
        </div>
      )}

      {error && (
        <div className="flex-1 flex items-center justify-center bg-red-50 text-red-600">
          <p>⚠️ Error loading map data: {error}</p>
        </div>
      )}

      {/* Map */}
      {!loading && !error && (
        <div className="flex-1">
          <MapContainer
            center={[15.15, 120.6]}
            zoom={13}
            className="w-full h-full"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />

            {data.map((item, idx) => (
              <React.Fragment key={idx}>
                <Marker position={[item.lat, item.lon]}>
                  <Popup>
                    <strong>{item.barangay}</strong>
                    <br />
                    {item.message}
                    <br />
                    Risk: {item.risk_label}
                    <br />
                    Status: {item.anomaly_label}
                    <br />
                    🌧️ Rain: {item.precip.toFixed(2)} mm
                    <br />
                    💧 Discharge: {item.river_discharge.toFixed(2)} m³/s
                  </Popup>
                </Marker>

                <Circle
                  center={[item.lat, item.lon]}
                  radius={
                    item.risk_label === "High"
                      ? 1000
                      : item.risk_label === "Medium"
                      ? 600
                      : 300
                  }
                  pathOptions={{
                    color: riskColors[item.risk_label] || "blue",
                    fillOpacity: 0.3,
                  }}
                />
              </React.Fragment>
            ))}
          </MapContainer>
        </div>
      )}
    </div>
  );
};

export default FloodMap;
