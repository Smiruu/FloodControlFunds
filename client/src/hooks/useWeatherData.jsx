import { useState, useEffect } from "react";

// Mock weather data per barangay in Angeles City
const mockWeatherData = [
  {
    barangay: "Balibago",
    temp: 31,
    feels_like: 33,
    humidity: 65,
    pressure: 1010,
    description: "sunny",
    icon: "01d",
    wind: 3.2,
  },
  {
    barangay: "Pampang",
    temp: 29,
    feels_like: 30,
    humidity: 72,
    pressure: 1011,
    description: "cloudy",
    icon: "02d",
    wind: 2.8,
  },
  {
    barangay: "Pulung Maragul",
    temp: 30,
    feels_like: 32,
    humidity: 68,
    pressure: 1012,
    description: "light rain",
    icon: "10d",
    wind: 4.1,
  },
  {
    barangay: "Cutcut",
    temp: 32,
    feels_like: 34,
    humidity: 60,
    pressure: 1009,
    description: "hot & humid",
    icon: "03d",
    wind: 3.5,
  },
  {
    barangay: "Santo Rosario",
    temp: 30,
    feels_like: 32,
    humidity: 66,
    pressure: 1010,
    description: "partly cloudy",
    icon: "02d",
    wind: 3.0,
  },
  {
    barangay: "Anunas",
    temp: 29,
    feels_like: 31,
    humidity: 70,
    pressure: 1011,
    description: "light showers",
    icon: "10d",
    wind: 4.0,
  },
  {
    barangay: "Pulung Cacutud",
    temp: 28,
    feels_like: 30,
    humidity: 75,
    pressure: 1013,
    description: "rainy",
    icon: "09d",
    wind: 3.8,
  },
  {
    barangay: "Sapangbato",
    temp: 27,
    feels_like: 29,
    humidity: 80,
    pressure: 1012,
    description: "thunderstorms",
    icon: "11d",
    wind: 5.2,
  },
  {
    barangay: "Pulung Bulu",
    temp: 31,
    feels_like: 33,
    humidity: 67,
    pressure: 1009,
    description: "sunny intervals",
    icon: "04d",
    wind: 2.5,
  },
  {
    barangay: "Capaya",
    temp: 30,
    feels_like: 32,
    humidity: 69,
    pressure: 1011,
    description: "humid & cloudy",
    icon: "03d",
    wind: 3.1,
  },
];

// 👉 you can add more barangays as needed

export default function useWeatherData() {
  const [weatherData, setWeatherData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // simulate API call delay
    const timer = setTimeout(() => {
      setWeatherData(mockWeatherData);
      setLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, []);

  return { weatherData, loading };
}
