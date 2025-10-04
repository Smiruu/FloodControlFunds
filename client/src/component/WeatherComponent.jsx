import React from "react";
import useWeatherData from "../hooks/useWeatherData";

function WeatherComponent() {
  const { weatherData, loading } = useWeatherData();

  if (loading) {
    return (
      <div className="p-4 text-center text-gray-500">
        Loading weather for barangays...
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {weatherData.map((barangay, idx) => (
        <div
          key={idx}
          className="bg-white p-4 rounded-xl shadow-md w-full"
        >
          <div className="text-md font-bold mb-2 text-gray-800">
            {barangay.barangay}
          </div>

          <div className="flex items-center space-x-4">
            <img
              src={`https://openweathermap.org/img/wn/${barangay.icon}@2x.png`}
              alt={barangay.description}
              className="w-12 h-12"
            />
            <div>
              <div className="text-xl font-bold">
                {barangay.temp}°C
              </div>
              <div className="capitalize text-gray-600">
                {barangay.description}
              </div>
            </div>
          </div>

          <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-gray-700">
            <div>
              <span className="font-semibold">Feels like:</span>{" "}
              {barangay.feels_like}°C
            </div>
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
              {barangay.wind} m/s
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default WeatherComponent;
