import React from "react";
import useMapData from "../hooks/useMap";

function WeatherComponent() {
  const { data, loading } = useMapData();

  if (loading) {
    return (
      <div className="p-4 text-center text-white bg-orange-500 rounded-xl shadow-md">
        Loading weather and flood data for barangays...
      </div>
    );
  }

  return (
    <div className="bg-orange-500 p-4 rounded-xl shadow-lg flex flex-col h-full">
      <div className="text-white font-bold text-xl mb-3">Barangay Weather</div>

      {/* Scrollable container filling the remaining space */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-3 scrollbar-thin scrollbar-thumb-white/30 scrollbar-track-orange-400 min-h-0">
        {data.map((barangay, idx) => (
          <div
            key={idx}
            className="bg-white p-4 rounded-xl shadow-md w-full transition hover:scale-[1.01] duration-200"
          >
            <div className="text-lg font-bold mb-2 text-gray-800">
              {barangay.barangay}
            </div>

            <div className="flex items-center justify-between mb-2">
              <div>
                <div className="text-lg font-bold text-blue-600">
                  {barangay.temp_min}°C – {barangay.temp_max}°C
                </div>
                <div className="text-gray-600 capitalize">
                  Precip: {barangay.precip} mm ({barangay.precip_prob}% chance)
                </div>
              </div>
              <div className="text-sm text-gray-500 text-right">
                Risk:{" "}
                <span
                  className={
                    barangay.risk_label === "High"
                      ? "text-red-600 font-semibold"
                      : barangay.risk_label === "Medium"
                      ? "text-blue-600 font-semibold"
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

            <div className="mt-2 text-sm text-gray-600 italic">
              {barangay.message}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WeatherComponent;
