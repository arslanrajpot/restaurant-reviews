"use client";

import { useEffect, useState } from "react";
import { get_user_data } from "@/service/api";
import { UserDataType } from "@/types/api";

const Header = () => {
  const [data, setData] = useState<UserDataType | null>(null);

  useEffect(() => {
    const fetch_data = async () => {
      try {
        const response = await get_user_data();
        setData(response);
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };
    fetch_data();
  }, []);

  return (
    <div className="bg-white shadow-xs">
      <div className="flex justify-end items-center px-6 py-4 border-b border-gray-300">
        <div className="flex items-center gap-3 px-4 py-2 rounded-lg  border border-blue-200 shadow">
          <div className="w-8 h-8 flex items-center justify-center rounded-full bg-[#5696a3] text-white font-bold text-lg">
            {data?.email
              ? data.email[0].toUpperCase()
              : data?.name
              ? data.name[0].toUpperCase()
              : "U"}
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-500">
              HI,{" "}
              <span className="font-semibold" style={{ color: '#5696a3' }}>
                {data?.email
                  ? data.email.split("@")[0].toUpperCase()
                  : data?.name.toUpperCase() || "User"}
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
