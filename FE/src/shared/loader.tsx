"use client";

import React from "react";
import Image from "next/image";
import logoImage from "@/assets/images/logo.png";

export default function Loader() {
    return (
      <div className="w-full h-[100vh] flex justify-center items-center">
          <div className="flex justify-center items-center">
            <Image
              src={logoImage}
              alt="Review Munch Logo"
              width={200} // set appropriate width
              height={80} // set appropriate height
              className="logo-zoom"
            />
          </div>
      </div>
    );
}
