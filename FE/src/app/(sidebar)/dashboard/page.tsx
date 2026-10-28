'use client'
import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { get_restaurant_data } from "@/service/api";
import {RestaurantDataResponse} from "@/types/api";
import { MdOutlineStorefront, MdOutlineRateReview, MdOutlineRestaurantMenu } from "react-icons/md";
import { FaStar } from "react-icons/fa";

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

  const COLORS = ["#C0392B", "#D98F30", "var(--button-theme)", "#4C8C96", "var(--color-theme)"];

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

  const statCards = [
    { label: "Restaurant Name", value: data.restaurant_name, icon: MdOutlineStorefront },
    { label: "Total Public Reviews", value: data.total_review_counts, icon: MdOutlineRateReview },
    { label: "Average Rating", value: `${data.overall_rating} / 5`, icon: FaStar },
    { label: "Top Rated Item", value: data.cuisine === "NaN" ? "-" : data.cuisine, icon: MdOutlineRestaurantMenu },
  ];

  return (
    <div className="flex flex-col xl:flex-row w-full min-h-[70vh] p-6 gap-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 xl:w-[55%]">
        {statCards.map(({ label, value, icon: Icon }) => (
          <div
            key={label}
            className="bg-white shadow-md rounded-2xl p-6 flex flex-col gap-3 hover:shadow-lg transition-shadow"
          >
            <div className="w-10 h-10 flex items-center justify-center rounded-xl bg-[var(--color-theme)]/10">
              <Icon className="text-xl" style={{ color: "var(--color-theme)" }} />
            </div>
            <h2 className="text-sm font-medium text-gray-500">{label}</h2>
            <p className="text-2xl font-bold truncate" style={{ color: "var(--button-theme)" }}>{value}</p>
          </div>
        ))}
      </div>

      <div className="xl:w-[45%] bg-white shadow-md rounded-2xl p-6 flex flex-col items-center justify-center">
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
