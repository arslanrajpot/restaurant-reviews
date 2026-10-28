"use client";

import React from "react";
import Logo from "@/components/Logo";

export default function Loader() {
    return (
      <div className="w-full h-[100vh] flex justify-center items-center">
          <div className="flex justify-center items-center">
            <Logo className="logo-zoom" />
          </div>
      </div>
    );
}
