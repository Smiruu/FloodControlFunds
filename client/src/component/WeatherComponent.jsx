import React from "react";
import useMapData from "../hooks/useMap";

function WeatherComponent() {
  const { data, loading } = useMapData();

  if (loading) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading weather and flood data for barangays...
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {data.map((barangay, idx) => (
        <div key={idx} className="bg-white p-4 rounded-xl shadow-md w-full">
          {/* Barangay name */}
          <div className="text-md font-bold mb-2 text-gray-800">
            {barangay.barangay}
          </div>

          {/* Weather summary */}
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="text-lg font-bold text-blue-600">
                {barangay.temp_min}°C – {barangay.temp_max}°C
              </div>
              <div className="text-gray-600 capitalize">
                Precip: {barangay.precip} mm ({barangay.precip_prob}% chance)
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Risk:{" "}
              <span
                className={
                  barangay.risk_label === "High"
                    ? "text-red-600 font-semibold"
                    : barangay.risk_label === "Medium"
                    ? "text-orange-500 font-semibold"
                    : "text-green-600 font-semibold"
                }
              >
                {barangay.risk_label}
              </span>
              <br />
              Status:{" "}
              <span
                className={
                  barangay.anomaly_label === "Normal"
                    ? "text-green-600 font-semibold"
                    : "text-yellow-600 font-semibold"
                }
              >
                {barangay.anomaly_label}
              </span>
            </div>
          </div>

          {/* Weather details */}
          <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
            <div>
              <span className="font-semibold">Humidity:</span>{" "}
              {barangay.humidity}%
            </div>
            <div>
              <span className="font-semibold">Pressure:</span>{" "}
              {barangay.pressure} hPa
            </div>
            <div>
              <span className="font-semibold">Wind:</span>{" "}
              {barangay.windspeed} m/s
            </div>
            <div>
              <span className="font-semibold">River Discharge:</span>{" "}
              {barangay.river_discharge}
            </div>
          </div>

          {/* Message from the AI */}
          <div className="mt-2 text-sm text-gray-600 italic">
            {barangay.message}
          </div>
        </div>
      ))}
    </div>
  );
}

export default WeatherComponent;
