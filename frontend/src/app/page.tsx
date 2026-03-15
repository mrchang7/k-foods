"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar, { Category } from "@/components/Sidebar";
import VideoGrid from "@/components/VideoGrid";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import ShortsCarousel from "@/components/ShortsCarousel";
import { Filter } from "lucide-react";

export default function Home() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [, setIsMobileMenuOpen] = useState(false);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // A shared setter that both Header and HeroSection can call
  const handleSearch = useCallback((q: string) => {
    setSearchQuery(q);
    // Clear category filters on any search or search-clear (e.g., Logo click)
    setSelectedCategories([]);
  }, []);

  // Wait until we have a proper use case for TrendingSection or remove if unused
  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
        const res = await fetch(`${apiBase}/api/categories`);
        if (res.ok) {
          const data = await res.json();
          setCategories(data);
        }
      } catch (error) {
        console.error("Failed to load categories", error);
      }
    };
    fetchCategories();
  }, []);

  const handleCategoryChange = (categoryId: number) => {
    // When selecting a category, clear search query
    if (searchQuery) setSearchQuery("");

    const targetCategory = categories.find((c) => c.category_id === categoryId);
    if (!targetCategory) return;

    setSelectedCategories((prev) => {
      // If already selected, just deselect it (toggle off)
      if (prev.includes(categoryId)) {
        return prev.filter((id) => id !== categoryId);
      }
      
      // Otherwise, remove any currently selected categories that share the same parent_id (same group)
      const sameGroupCategoryIds = categories
        .filter((c) => c.parent_id === targetCategory.parent_id)
        .map((c) => c.category_id);
        
      const newSelection = prev.filter((id) => !sameGroupCategoryIds.includes(id));
      
      // Add the newly selected category
      return [...newSelection, categoryId];
    });
  };

  const handleRemoveCategory = (categoryId: number) => {
    setSelectedCategories(prev => prev.filter(id => id !== categoryId));
  };

  const isBrowsingMode = selectedCategories.length === 0 && searchQuery === "";

  return (
    <div className="bg-[#141414] min-h-screen text-white font-sans flex flex-col">
      <Header
        categories={categories}
        onMenuClick={() => setIsMobileMenuOpen(true)}
        onSearch={handleSearch}
      />

      {/* Always show Search Hero */}
      <HeroSection onSearch={handleSearch} />

      <div className="flex flex-1 max-w-[1600px] w-full mx-auto relative">
        {/* Desktop Sidebar */}
        <div className="hidden md:block">
          <Sidebar
            categories={categories}
            selectedCategories={selectedCategories}
            onChange={handleCategoryChange}
          />
        </div>

        {/* Mobile Filter Modal/Drawer (Simplified for this demo) */}
        {isMobileFilterOpen && (
          <div className="fixed inset-0 z-50 bg-[#141414] md:hidden overflow-y-auto">
            <div className="p-4 flex justify-between items-center border-b border-gray-800">
              <h2 className="text-xl font-bold">필터</h2>
              <button onClick={() => setIsMobileFilterOpen(false)} className="text-gray-400 p-2">닫기</button>
            </div>
            <Sidebar
              categories={categories}
              selectedCategories={selectedCategories}
              onChange={handleCategoryChange}
            />
          </div>
        )}

        <main id="main-dishes-section" className="flex-1 flex flex-col border-l border-gray-800">
          <VideoGrid
            categories={categories}
            selectedCategories={selectedCategories}
            onRemoveCategory={handleRemoveCategory}
            excludeVideoIds={[]}
            searchQuery={searchQuery}
            onClearSearch={() => handleSearch("")}
            showShorts={false}
          />
        </main>
      </div>

      {/* Floating Action Button for Mobile Filter */}
      <button
        onClick={() => setIsMobileFilterOpen(true)}
        className="md:hidden fixed bottom-6 right-6 w-14 h-14 bg-red-600 rounded-full shadow-lg flex items-center justify-center text-white z-40 hover:bg-red-700 transition-colors"
      >
        <Filter size={24} />
      </button>
    </div>
  );
}
