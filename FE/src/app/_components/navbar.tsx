"use client";

import { usePathname } from "next/navigation";

const Navbar = () => {
  const currentPath = usePathname();

  const isSettingPage = (route: string) => currentPath === route;
  const isReviewAgentPage = (route: string) => currentPath === route;

  return (
    <div className="w-full">
      <div className="flex justify-between items-center p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 pl-4">
            <span className="text-2xl font-semibold text-gray-800">
              {isSettingPage("/setting") ? "Settings" : isReviewAgentPage("/review_agent") ? "Review Agent": "Dashboard"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
