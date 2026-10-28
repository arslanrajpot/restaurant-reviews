"use client";

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from "next/navigation";
import Sidebar from "@/app/_components/sidebar";
import Navbar from "@/app/_components/navbar";
import Header from "@/app/_components/header";
import Loader from "@/shared/loader";

const SidebarLayout = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  const pathname = usePathname();
  const isAuthPage = pathname.endsWith('/login') || pathname.endsWith('signup');
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const NavbarPages = pathname !== '/agents';

  useEffect(() => {
    const auth_token = localStorage.getItem("authToken");

    // If no auth token and the user is not on an auth page, redirect to login
    if (!auth_token && !isAuthPage) {
      router.push("/login"); // Redirect to login
    } else {
      setLoading(false); // Set loading to false only if the check completes
    }
  }, [router, isAuthPage]);

  // If loading, render nothing (no flicker of the page)
  if (loading) {
    return <Loader />;
  }

  return (
    <div className="flex h-screen">
      {!isAuthPage && (
        <div className={`w-64 transition-all`}>
          <Sidebar />
        </div>
      )}

      <div className={`flex-1 ${isAuthPage ? 'bg-gray-100' : 'bg-gray-50'} min-h-screen`}>
        <Header />
        {NavbarPages && <Navbar />}
        <div className={`flex-1 p-6 bg-white rounded-lg ${NavbarPages ? 'h-[80vh] mx-6' : 'h-[85vh] mx-6 mt-6'}`}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default SidebarLayout;
