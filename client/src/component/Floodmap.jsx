import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import useMapData from "../hooks/useMap"; // 👈 use the custom hook

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
  const data = useMapData(); // 👈 fetch + cache logic here

  const riskColors = {
    Low: "green",
    Medium: "orange",
    High: "red",
  };

  return (
    <div
      style={{
        border: "2px solid #ccc",
        borderRadius: "12px",
        overflow: "hidden",
        width: "600px",
        height: "400px",
        margin: "0 auto",
      }}
    >
      <MapContainer center={[15.15, 120.6]} zoom={12} style={{ height: "100vh", width: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {data.map((item, idx) => (
          <React.Fragment key={idx}>
            <Marker position={[item.lat, item.lon]}>
              <Popup>
                <strong>{item.barangay}</strong><br />
                {item.message}<br />
                Risk: {item.risk_label}<br />
                Status: {item.anomaly_label}
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
  );
};

export default FloodMap;
