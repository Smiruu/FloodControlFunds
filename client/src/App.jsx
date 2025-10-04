import { useState } from "react";
import WeatherComponent from "./component/WeatherComponent";
import "./index.css";
import FloodMap from "./component/Floodmap";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div className="h-screen flex flex-col bg-gray-100">
        {/* Header */}
        <div className="bg-white p-2 rounded-xl shadow-lg m-4">
          <p className="text-lg font-bold text-gray-800">Flood Alert</p>
        </div>

        {/* Main content fills rest of screen */}
        <div className="grid grid-cols-5 gap-6 m-4 flex-1 overflow-hidden">
          {/* Left column - Map */}
          <div className="col-span-3 bg-white p-4 rounded-xl shadow-lg flex flex-col overflow-hidden">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Flood Map</h2>
            <div className="flex-1 overflow-hidden">
              <FloodMap />
            </div>
          </div>

          {/* Right column - Weather */}
          <div className="col-span-2 bg-white p-4 rounded-xl shadow-lg overflow-y-auto">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Weather per Barangay
            </h2>
            <WeatherComponent />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
