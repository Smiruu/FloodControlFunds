import { useState, useEffect } from "react";
import axios from "axios";

const STORAGE_KEY = "floodData";

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

        // ✅ Use cache if same date
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed.date === today) {
            setData(parsed.data);
            setLoading(false);
            return;
          }
        }

        // ✅ Otherwise fetch fresh data
        const res = await axios.get("http://127.0.0.1:5000/predict_all");
        setData(res.data);

        // ✅ Save new data to localStorage
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
