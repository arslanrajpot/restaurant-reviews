"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Loader from "@/shared/loader";

export default function Home() {
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const auth_token = localStorage.getItem("authToken");
    if (auth_token) {
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
    setLoading(false);
  }, [router]);

  if (loading) {
    return (
      <Loader />
    );
  }
  return null;
}
