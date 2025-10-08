import { useState } from "react";
import WeatherComponent from "./component/WeatherComponent";
import "./index.css";
import FloodMap from "./component/Floodmap";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-white p-4 rounded-xl shadow-lg m-4 text-center">
        <h1 className="text-2xl font-extrabold">
          <span className="text-orange-500">Flood</span>
          <span className="text-black">Sight</span>
        </h1>
        <p className="text-sm text-gray-600 font-medium mt-1">Here To Serve</p>
      </div>

      {/* Responsive main grid */}
      <div className="flex-1 m-4 grid grid-cols-1 lg:grid-cols-5 gap-6 overflow-hidden">
        {/* Left column - Map */}
        <div className="lg:col-span-3 bg-white p-4 rounded-xl shadow-lg flex flex-col overflow-hidden">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Flood Map</h2>
          <div className="flex-1 overflow-hidden">
            <FloodMap />
          </div>
        </div>

        {/* Right column - Weather */}
        <div className="lg:col-span-2 bg-white p-4 rounded-xl shadow-lg overflow-y-auto max-h-[600px]">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Weather per Barangay
          </h2>
          <WeatherComponent />
        </div>
      </div>
    </div>
  );
}

export default App;
