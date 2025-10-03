import { useState, useEffect } from "react";
import axios from "axios";

const STORAGE_KEY = "floodData";

export default function useMapData() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
        const cached = localStorage.getItem(STORAGE_KEY);

        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed.date === today) {
            setData(parsed.data); // ✅ load cached data
            return;
          }
        }

        // ✅ Fetch fresh data if not cached or date mismatch
        const res = await axios.get("http://127.0.0.1:5000/predict_all");
        setData(res.data);

        // ✅ Save to localStorage with today's date
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({ date: today, data: res.data })
        );
      } catch (err) {
        console.error("Error fetching flood map data:", err);
      }
    };

    fetchData();
  }, []);

  return data;
}
