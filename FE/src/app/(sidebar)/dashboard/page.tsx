'use client'
import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { get_restaurant_data } from "@/service/api";
import {RestaurantDataResponse} from "@/types/api";

export default function Home() {
  const [data, setData] = useState<RestaurantDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [pieData, setPieData] = useState([
    { name: "1 Star", value: 0 },
    { name: "2 Stars", value: 0 },
    { name: "3 Stars", value: 0 },
    { name: "4 Stars", value: 0 },
    { name: "5 Stars", value: 0 },
  ]);

  useEffect(() => {
    const fetch_data = async () => {
      try {
        const response = await get_restaurant_data();
        setData(response);
        setPieData([
          { name: "1 Star", value: response.one_stars },
          { name: "2 Stars", value: response.two_stars },
          { name: "3 Stars", value: response.three_stars },
          { name: "4 Stars", value: response.four_stars },
          { name: "5 Stars", value: response.five_stars },
        ]);
      } catch (err) {
        console.error("Error fetching restaurant data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetch_data();
  }, []);

  const COLORS = ["#FF4D4D", "#FF8042", "#FFBB28", "#00C49F", "#0088FE"];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh] w-full">
        <p className="text-gray-600 text-lg">Loading restaurant data...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[70vh] w-full">
        <p className="text-red-600 text-lg">Failed to load data.</p>
      </div>
    );
  }

  return (
    <div className="flex w-full h-[70vh] p-6 gap-6">
      <div className="flex flex-col gap-6 w-[60%]">
        <div className="bg-white rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-gray-700">Restaurant Name</h2>
          <p className="text-3xl font-bold mt-2">{data.restaurant_name}</p>
        </div>
        <div className="bg-white shadow-md rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-gray-700">Total Public Reviews</h2>
          <p className="text-3xl font-bold mt-2">{data.total_review_counts}</p>
        </div>
        <div className="bg-white shadow-md rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-gray-700">Average Rating</h2>
          <p className="text-3xl font-bold mt-2">{data.overall_rating} ⭐</p>
        </div>
        <div className="bg-white shadow-md rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-gray-700">Top Rated Item</h2>
          <p className="text-3xl font-bold mt-2">{data.cuisine == "NaN" ? "-" : data.cuisine}</p>
        </div>
      </div>

      <div className="w-full bg-white shadow-md rounded-2xl p-6 flex flex-col items-center justify-center">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Ratings Breakdown</h2>
        <ResponsiveContainer width="100%" height={420}>
          <PieChart>
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={150}
              label
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
