import { useState, useEffect } from "react";
import axios from "axios";

const STORAGE_KEY = "floodData";
const API_URL = import.meta.env.VITE_API_URL; // ✅ from env file

export default function useMapData() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
        const cached = localStorage.getItem(STORAGE_KEY);

        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed.date === today) {
            setData(parsed.data);
            setLoading(false);
            return;
          }
        }

        const res = await axios.get(`${API_URL}/predict_all`);
        setData(res.data);

        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({ date: today, data: res.data })
        );
      } catch (err) {
        console.error("Error fetching flood map data:", err);
        setError(err.message || "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
}
