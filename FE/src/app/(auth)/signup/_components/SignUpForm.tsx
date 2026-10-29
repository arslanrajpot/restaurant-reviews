"use client";

import React, { useEffect, useState, useRef } from "react";
import { IoEyeOff, IoEye } from "react-icons/io5";
import { get_restaurant_names, signup } from "@/service/api";
import { useRouter } from "next/navigation";
import { RestaurantResponseType } from "@/types/api";
import Logo from "@/components/Logo";

export default function SignUpForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone_number: "",
    restaurant_id: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isChecked, setIsChecked] = useState(false);
  const [confirmed, setConfirmed] = useState("");
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState("");
  const passwordLengthValid =
    formData.password.length >= 6 && formData.password.length <= 20;
  const passwordUppercaseValid = /[A-Z]/.test(formData.password);
  const passwordLowercaseValid = /[a-z]/.test(formData.password);
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const passwordNumberValid = /\d/.test(formData.password);
  const passwordSpecialCharValid = /[@$!%*?&]/.test(formData.password);
  const [error, setError] = useState({
    password: "",
  });
  const [restaurantList, setRestaurantList] = useState<
    RestaurantResponseType[]
  >([]);
  const [showModal, setShowModal] = useState(false);
  const [modalForm, setModalForm] = useState({ name: "", location: "" });
  const [modalErrors, setModalErrors] = useState({
    name: "",
    location: "",
    general: "",
  });
  const [modalLoading, setModalLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<RestaurantResponseType[]>(
    []
  );
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedRestaurant, setSelectedRestaurant] =
    useState<RestaurantResponseType | null>(null);
  const [availableLocations, setAvailableLocations] = useState<string[]>([]);
  const [filteredLocations, setFilteredLocations] = useState<string[]>([]);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [locationInputValue, setLocationInputValue] = useState("");
  const [isRestaurantFromDatabase, setIsRestaurantFromDatabase] =
    useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const locationDropdownRef = useRef<HTMLDivElement>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    if (name === "restaurant_id" && value === "search_restaurant") {
      setShowModal(true);
      return;
    }
    if (name === "confirmed_password") {
      setConfirmed(value);
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
    setErrors("");
  };

  const resetModalState = () => {
    setModalForm({ name: "", location: "" });
    setModalErrors({ name: "", location: "", general: "" });
    setSelectedRestaurant(null);
    setSearchResults([]);
    setShowDropdown(false);
    setAvailableLocations([]);
    setFilteredLocations([]);
    setShowLocationDropdown(false);
    setLocationInputValue("");
    setIsRestaurantFromDatabase(false);
  };

  const getUniqueRestaurants = (filterText?: string) => {
    const lowerFilter = filterText?.trim().toLowerCase();
    return restaurantList.reduce((acc: RestaurantResponseType[], current) => {
      const exists = acc.find(
        (item) => item.name.toLowerCase() === current.name.toLowerCase()
      );
      if (
        !exists &&
        (!lowerFilter || current.name.toLowerCase().includes(lowerFilter))
      ) {
        acc.push(current);
      }
      return acc;
    }, []);
  };

  const handleRestaurantNameChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    setModalForm((prev) => ({ ...prev, name: value }));
    setModalErrors((prev) => ({ ...prev, name: "", general: "" }));
    setSelectedRestaurant(null);
    setAvailableLocations([]);
    setFilteredLocations([]);
    setShowLocationDropdown(false);
    setLocationInputValue("");
    setModalForm((prev) => ({ ...prev, location: "" }));
    setIsRestaurantFromDatabase(false);

    const uniqueRestaurants = getUniqueRestaurants(value);
    setSearchResults(uniqueRestaurants);
    setShowDropdown(uniqueRestaurants.length > 0);

    if (value.trim()) {
      const lowerValue = value.toLowerCase();
      const matchedLocations = restaurantList
        .filter((r) => r.name.toLowerCase() === lowerValue)
        .map((r) => r.location)
        .filter(
          (location): location is string =>
            typeof location === "string" && location.trim() !== ""
        )
        .filter((location, index, self) => self.indexOf(location) === index);
      setAvailableLocations(matchedLocations);
      setSelectedRestaurant({
        id: "",
        name: value,
        location: "",
      });
    } else {
      setAvailableLocations([]);
      setSelectedRestaurant(null);
    }
  };

  const handleRestaurantSelect = async (restaurant: RestaurantResponseType) => {
    setSelectedRestaurant(restaurant);
    setModalForm((prev) => ({ ...prev, name: restaurant.name, location: "" }));
    setShowDropdown(false);
    setSearchResults([]);
    setIsRestaurantFromDatabase(true); // Mark as selected from database

    // Clear all location-related states when restaurant is from database
    setAvailableLocations([]);
    setLocationInputValue("");
    setFilteredLocations([]);
    setShowLocationDropdown(false);
  };

  const handleLocationInputChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    setLocationInputValue(value);
    setModalForm((prev) => ({ ...prev, location: value }));
    setModalErrors((prev) => ({ ...prev, location: "", general: "" }));

    if (value.trim() && availableLocations.length > 0) {
      const filtered = availableLocations.filter((location) =>
        location.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredLocations(filtered);
      setShowLocationDropdown(filtered.length > 0);
    } else if (availableLocations.length > 0) {
      setFilteredLocations(availableLocations);
      setShowLocationDropdown(true);
    } else {
      setFilteredLocations([]);
      setShowLocationDropdown(false);
    }
  };

  const handleLocationSelect = (location: string) => {
    setLocationInputValue(location);
    setModalForm((prev) => ({ ...prev, location }));
    setShowLocationDropdown(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
      if (
        locationDropdownRef.current &&
        !locationDropdownRef.current.contains(event.target as Node)
      ) {
        setShowLocationDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalForm.name.trim()) {
      setModalErrors({
        name: "Restaurant name is required",
        location: "",
        general: "",
      });
      return;
    }

    try {
      setModalLoading(true);

      const existingRestaurant = restaurantList.find(
        (r) =>
          r.name.toLowerCase() === modalForm.name.toLowerCase() &&
          (!modalForm.location ||
            !r.location ||
            r.location.toLowerCase() === modalForm.location.toLowerCase())
      );

      if (existingRestaurant) {
        setFormData((prev) => ({
          ...prev,
          restaurant_id: existingRestaurant.id,
        }));
        setShowModal(false);
        resetModalState();
        return;
      }

      // This demo only serves a fixed set of seeded restaurants — live
      // lookups (SerpAPI + RAG indexing) stay off the public signup page.
      setModalErrors((prev) => ({
        ...prev,
        general:
          "This demo includes a preset list of restaurants. Please choose one from the dropdown above.",
      }));
    } finally {
      setModalLoading(false);
    }
  };

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        const response = await get_restaurant_names();
        setRestaurantList(response);
      } catch (error) {
        console.error("Error fetching restaurants:", error);
      }
    };
    fetchRestaurants();
  }, []);

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setIsChecked(event.target.checked);
  };

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!isChecked) {
      setErrors("Please agree to the terms and conditions.");
      return;
    }
    const newErrors = { password: "", confirmed_password: "" };

    if (!formData.password.trim()) {
      newErrors.password = "This field is required";
    } else if (
      !passwordLengthValid ||
      !passwordUppercaseValid ||
      !passwordLowercaseValid ||
      !passwordNumberValid ||
      !passwordSpecialCharValid
    ) {
      setErrors("Password must meet all criteria.");
      return;
    }

    if (!confirmed.trim()) {
      newErrors.confirmed_password = "This field is required";
    } else if (formData.password !== confirmed) {
      newErrors.confirmed_password = "Passwords do not match";
    }
    if (newErrors.password || newErrors.confirmed_password) {
      if (newErrors.password) {
        setError(newErrors);
      } else {
        setErrors(newErrors.confirmed_password);
      }
      return;
    }
    try {
      setIsButtonDisabled(true);
      await signup(formData);
      router.push("/subscription");
    } catch (err) {
      setErrors(
        (err as Error).message || "Invalid credentials. Please try again."
      );
      setIsButtonDisabled(false);
    }
  };

  return (
    <>
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-6 relative">
            {modalLoading && (
              <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-xl flex items-center justify-center z-10">
                <div className="flex flex-col items-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--button-theme)]"></div>
                  <p className="mt-4 text-gray-600 font-medium">
                    Searching restaurant...
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Please wait while we fetch the data
                  </p>
                </div>
              </div>
            )}
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Search Restaurant
            </h2>
            {modalErrors.general && (
              <p className="text-red-500 text-sm mb-4">{modalErrors.general}</p>
            )}
            <form onSubmit={handleModalSubmit}>
              <div className="mb-4 relative" ref={dropdownRef}>
                <label className="block text-gray-700 mb-2">
                  Restaurant Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={modalForm.name}
                  onChange={handleRestaurantNameChange}
                  onFocus={() => {
                    const uniqueRestaurants = getUniqueRestaurants(
                      modalForm.name
                    );
                    if (uniqueRestaurants.length > 0) {
                      setSearchResults(uniqueRestaurants);
                      setShowDropdown(true);
                    }
                  }}
                  className="w-full p-2 border rounded-md focus:ring focus:outline-none"
                  placeholder="Click to see available restaurants"
                  disabled={modalLoading}
                  autoComplete="off"
                />
                {modalErrors.name && (
                  <p className="text-red-500 text-sm mt-1">
                    {modalErrors.name}
                  </p>
                )}
                {showDropdown && searchResults.length > 0 && !modalLoading && (
                  <div className="absolute z-20 w-full mt-2 bg-white border-0 rounded-lg shadow-xl max-h-60 overflow-hidden">
                    <div className="py-2">
                      <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide bg-gray-50 border-b">
                        Available Restaurants ({searchResults.length})
                      </div>
                      <div className="max-h-48 overflow-y-auto">
                        {searchResults.slice(0, 10).map((restaurant, index) => (
                          <div
                            key={`${restaurant.id}-${index}`}
                            className="group relative px-4 py-3 hover:bg-blue-50 cursor-pointer transition-all duration-150 ease-in-out border-b border-gray-100 last:border-b-0"
                            onMouseDown={(e) => {
                              e.preventDefault();
                              handleRestaurantSelect(restaurant);
                            }}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="font-medium text-gray-900 group-hover:text-blue-700 transition-colors duration-150">
                                  {restaurant.name}
                                </div>
                                {restaurant.location && (
                                  <div className="text-sm text-gray-500 mt-1 flex items-center">
                                    <svg
                                      className="w-3 h-3 mr-1 opacity-60"
                                      fill="currentColor"
                                      viewBox="0 0 20 20"
                                    >
                                      <path
                                        fillRule="evenodd"
                                        d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9z"
                                        clipRule="evenodd"
                                      />
                                    </svg>
                                    {restaurant.location}
                                  </div>
                                )}
                              </div>
                              <div className="ml-3 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                                <svg
                                  className="w-4 h-4 text-blue-500"
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 5l7 7-7 7"
                                  />
                                </svg>
                              </div>
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-150"></div>
                          </div>
                        ))}
                      </div>
                      {searchResults.length > 10 && (
                        <div className="px-4 py-2 text-xs text-gray-500 bg-gray-50 border-t">
                          Showing first 10 results. Keep typing to narrow
                          down...
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <div className="mb-4 relative" ref={locationDropdownRef}>
                <label className="block text-gray-700 mb-2">
                  Location {!isRestaurantFromDatabase && "*"}
                </label>
                <input
                  type="text"
                  name="location"
                  value={isRestaurantFromDatabase ? "" : locationInputValue}
                  onChange={handleLocationInputChange}
                  onFocus={() => {
                    if (
                      !isRestaurantFromDatabase &&
                      availableLocations.length > 0
                    ) {
                      setFilteredLocations(availableLocations);
                      setShowLocationDropdown(true);
                    }
                  }}
                  placeholder={
                    isRestaurantFromDatabase
                      ? "Enter Location"
                      : selectedRestaurant
                      ? availableLocations.length > 0
                        ? "Start typing or select from dropdown..."
                        : "Enter Location"
                      : "Select a Restaurant First"
                  }
                  className={`w-full p-2 border rounded-md focus:ring focus:outline-none ${
                    isRestaurantFromDatabase
                      ? "bg-gray-100 cursor-not-allowed text-gray-400"
                      : ""
                  }`}
                  disabled={
                    modalLoading ||
                    !selectedRestaurant ||
                    isRestaurantFromDatabase
                  }
                  autoComplete="off"
                />
                {modalErrors.location && !isRestaurantFromDatabase && (
                  <p className="text-red-500 text-sm mt-1">
                    {modalErrors.location}
                  </p>
                )}
                {!isRestaurantFromDatabase &&
                  showLocationDropdown &&
                  filteredLocations.length > 0 &&
                  !modalLoading && (
                    <div className="absolute z-20 w-full mt-1 bg-white border rounded-md shadow-lg max-h-48 overflow-y-auto">
                      {filteredLocations.map((location, index) => (
                        <div
                          key={`${location}-${index}`}
                          className="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                          onMouseDown={(e) => {
                            e.preventDefault();
                            handleLocationSelect(location);
                          }}
                        >
                          <div className="text-gray-800">{location}</div>
                        </div>
                      ))}
                    </div>
                  )}
                {selectedRestaurant && isRestaurantFromDatabase && (
                  <p className="text-sm text-gray-500 mt-1"></p>
                )}
                {selectedRestaurant &&
                  !isRestaurantFromDatabase &&
                  availableLocations.length === 0 && (
                    <p className="text-sm text-gray-500 mt-1">
                      Location not found, Enter manually
                    </p>
                  )}
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetModalState();
                  }}
                  className="flex-1 p-2 border rounded-md hover:bg-gray-50 transition-colors"
                  disabled={modalLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 p-2 bg-[var(--button-theme)] text-white rounded-md hover:bg-[var(--button-theme)]/90 transition-colors disabled:opacity-50"
                  disabled={modalLoading || !modalForm.name.trim()}
                >
                  {modalLoading ? "Sending..." : "Send"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      <div className="w-full lg:w-2/3 h-full flex justify-center bg-white flex-col px-6 sm:px-10 md:px-16 lg:pl-20 py-12">
        <div className="w-full max-w-lg space-y-6 mx-auto lg:mx-0">
          <div className="flex justify-center items-center lg:justify-start">
            <Logo className="w-50" />
          </div>
          <h2 className="text-2xl text-gray-900">Sign Up</h2>
          <p className="text-gray-600 mt-[-20px]">
            Enter your credentials to create an account
          </p>
          {errors && <p className="text-red-500 text-sm mt-1">{errors}</p>}
          <form onSubmit={handleSubmit}>
            <div>
              <label className="block text-gray-700">Full Name</label>
              <input
                type="text"
                className="outline-[var(--button-theme)]/40 w-full p-2 mb-4 mt-1 text-black border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30"
                placeholder="Enter your full name"
                name="name"
                required={true}
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-gray-700">Email</label>
              <input
                type="email"
                className="outline-[var(--button-theme)]/40 w-full p-2 mb-4 mt-1 text-black border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30"
                placeholder="Enter your email"
                name="email"
                required={true}
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-gray-700">Phone Number</label>
              <input
                type="text"
                className="outline-[var(--button-theme)]/40 w-full p-2 mb-4 mt-1 text-black border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30"
                placeholder="Enter your phone number"
                name="phone_number"
                required={true}
                value={formData.phone_number}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="block text-gray-700">Restaurant</label>
              <div
                onClick={() => setShowModal(true)}
                className="outline-[var(--button-theme)]/40 w-full p-2 mb-4 mt-1 text-gray-500 border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                {formData.restaurant_id
                  ? restaurantList.find((r) => r.id === formData.restaurant_id)
                      ?.name || "Select Restaurant"
                  : "Select Restaurant"}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-gray-700">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    className="outline-[var(--button-theme)]/40 w-full p-2 mb-3 text-black border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30"
                    placeholder="Enter your password"
                    required={true}
                    value={formData.password}
                    onChange={handleChange}
                  />
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setShowPassword(!showPassword);
                    }}
                  >
                    {showPassword ? (
                      <IoEyeOff className="text-2xl pr-1 absolute top-3 inset-y-0 right-2 text-gray-500 cursor-pointer" />
                    ) : (
                      <IoEye className="text-2xl pr-1 absolute top-3 inset-y-0 right-2 text-gray-500 cursor-pointer" />
                    )}
                  </button>
                </div>
                {error.password && (
                  <p className="text-red-500 text-sm mt-1">{error.password}</p>
                )}
              </div>
              <div>
                <label className="block text-gray-700">
                  Confirmed Password
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmed_password"
                    className="outline-[var(--button-theme)]/40 w-full p-2 mb-3 text-black border border-[#D9D9D9] rounded-md focus:ring focus:ring-[var(--button-theme)]/30"
                    placeholder="Enter your password"
                    required={true}
                    value={confirmed}
                    onChange={handleChange}
                  />
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setShowConfirmPassword(!showConfirmPassword);
                    }}
                  >
                    {showConfirmPassword ? (
                      <IoEyeOff className="text-2xl pr-1 absolute top-3 inset-y-0 right-2 text-gray-500 cursor-pointer" />
                    ) : (
                      <IoEye className="text-2xl pr-1 absolute top-3 inset-y-0 right-2 text-gray-500 cursor-pointer" />
                    )}
                  </button>
                </div>
              </div>
            </div>
            {formData.password &&
              !(
                passwordLengthValid &&
                passwordUppercaseValid &&
                passwordLowercaseValid &&
                passwordNumberValid &&
                passwordSpecialCharValid
              ) && (
                <ul className="list-disc ml-5 mb-5 text-sm">
                  <li
                    className={`${
                      passwordLengthValid ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    Password should be 6 to 20 characters long.
                  </li>
                  <li
                    className={`${
                      passwordUppercaseValid &&
                      passwordLowercaseValid &&
                      passwordNumberValid
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
                    At least one digit, uppercase & lowercase letter.
                  </li>
                  <li
                    className={`${
                      passwordSpecialCharValid
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
                    At least one special character (@, $, !, %, *, ?, &).
                  </li>
                </ul>
              )}
            <div className="flex items-center space-x-1 mt-6">
              <input
                type="checkbox"
                id="terms"
                className="w-4 h-4 border-gray-300 rounded"
                onChange={handleCheckboxChange}
              />
              <label htmlFor="terms" className="text-gray-700 text-sm">
                I agree to the Terms of Service and Privacy Policy.
              </label>
            </div>
            <button
              className="w-full mt-10 p-2 bg-[var(--button-theme)] text-white rounded-full hover:bg-[var(--button-theme)]/80 cursor-pointer disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              disabled={
                !(
                  passwordLengthValid &&
                  passwordUppercaseValid &&
                  passwordLowercaseValid &&
                  passwordNumberValid &&
                  passwordSpecialCharValid
                ) || isButtonDisabled
              }
            >
              Sign Up
            </button>
          </form>
          <p className="text-center text-gray-600">
            Already have an account?<span> </span>
            <a href="/login" className="text-[var(--button-theme)]">
              Login
            </a>
          </p>
        </div>
      </div>
    </>
  );
}
