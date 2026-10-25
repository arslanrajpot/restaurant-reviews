"use client";

import { BsStars } from "react-icons/bs";
import { IoMdExit } from "react-icons/io";
import { RiSettingsLine } from "react-icons/ri";
import { IoHomeOutline } from "react-icons/io5";
import {usePathname, useRouter} from "next/navigation";
import Image from "next/image";
import logoImage from "@/assets/images/logo.png";


const Sidebar = () => {
  const router = useRouter();

  const handleButtonClick = (button: string, path: string) => {
    router.push(path);
  };
  const currentPath = usePathname();
  const isActive = (route: string) => {
   if (route === "/") return currentPath === "/";
   return currentPath.startsWith(route);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    router.push("/login");
  };


  return (
    <div className="w-64 pl-4 pr-4 bg-[var(--color-theme)] text-white transition-all duration-300 h-screen overflow-hidden flex flex-col">
      <nav className="flex-grow mt-[50px]">
        <div className="flex justify-center items-center">
          <Image
            src={logoImage}
            alt="Review Munch Logo"
            width={200} // set appropriate width
            height={80} // set appropriate height
            className="w-35"
          />
        </div>
        <div className="flex flex-col justify-center items-center mt-[50px]">
          <ul className="w-full">
            <li className="mb-4">
              <button
                className={`cursor-pointer flex items-center w-full p-2 rounded-lg hover:bg-[#accdd4]/40 ${
                  isActive("/dashboard") ? "bg-[#accdd4]/30" : ""
                }`}
                onClick={() => handleButtonClick("Home", "/dashboard")}
              >
                <IoHomeOutline className="text-2xl ml-4" />
                <span className="ml-4">Dashboard</span>
              </button>
            </li>
            <li className="mb-4">
              <button
                className={`cursor-pointer flex items-center w-full p-2 rounded-lg hover:bg-[#accdd4]/40 ${
                  isActive("/review_agent") ? "bg-[#accdd4]/30" : ""
                }`}
                onClick={() => handleButtonClick("aiAssistant", "/review_agent")}
              >
                <BsStars className="text-2xl ml-4" />
                <span className="ml-4">Review Agent</span>
              </button>
            </li>
            <li className="mb-4">
              <button
                className={`cursor-pointer flex items-center w-full p-2 rounded-lg hover:bg-[#accdd4]/40 ${
                  isActive("/setting") ? "bg-[#accdd4]/30" : ""
                }`}
                onClick={() => handleButtonClick("setting", "/setting")}
              >
                <RiSettingsLine className="text-2xl ml-4" />
                <span className="ml-4">Settings</span>
              </button>
            </li>
          </ul>
        </div>
      </nav>
      <div className="mt-auto mb-4">
        <button
          className={`cursor-pointer flex items-center w-full p-2 rounded-lg hover:bg-[#accdd4]/40`}
          onClick={handleLogout}
        >
          <IoMdExit className="text-2xl ml-4" />
          <span className="ml-4">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
