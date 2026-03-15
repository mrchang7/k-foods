"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar, { Category } from "@/components/Sidebar";
import VideoGrid from "@/components/VideoGrid";
import Header from "@/components/Header";
import { Filter, Search } from "lucide-react";

export default function ShortsPage() {
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
        setSelectedCategories((prev) =>
            prev.includes(categoryId)
                ? prev.filter((id) => id !== categoryId) // Remove
                : [...prev, categoryId]                  // Add
        );
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

            {/* Shorts Page Title Header (instead of HeroSection) */}
            <div className="w-full bg-[#1a1a1a] border-b border-gray-800 py-6 flex flex-col items-center justify-center text-center">
                    <h1 className="text-2xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500 mb-2 tracking-tight">
                        📱 1분 뚝딱! 쇼츠 레시피
                    </h1>
                    <p className="text-gray-400 max-w-2xl px-4 text-sm md:text-base mb-5">
                        바쁜 현대인을 위한 <span className="text-white font-medium">초간단 숏폼 레시피 모음</span>입니다.<br className="hidden sm:block" /> 빠르게 핵심만 배워서 오늘 저녁을 뚝딱 완성해 보세요!
                    </p>

                    {/* Search Bar */}
                    <div className="w-full max-w-xl px-4 relative group">
                        <div className="absolute inset-y-0 left-8 flex items-center pointer-events-none">
                            <Search className="w-5 h-5 text-gray-400 group-focus-within:text-white transition-colors" />
                        </div>
                        <input
                            type="text"
                            placeholder="레시피, 재료, 요리명 검색..."
                            className="w-full bg-[#141414] border border-gray-700 text-white placeholder-gray-500 text-base rounded-full py-2.5 pl-12 pr-6 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all shadow-inner"
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                        />
                    </div>
                </div>

            <div className="flex flex-1 max-w-[1600px] w-full mx-auto relative">
                {/* Desktop Sidebar */}
                <div className="hidden md:block">
                    <Sidebar
                        categories={categories}
                        selectedCategories={selectedCategories}
                        onChange={handleCategoryChange}
                    />
                </div>

                {/* Mobile Filter Modal/Drawer */}
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

                <main className="flex-1 border-l border-gray-800">
                    <VideoGrid
                        categories={categories}
                        selectedCategories={selectedCategories}
                        onRemoveCategory={handleRemoveCategory}
                        excludeVideoIds={[]}
                        searchQuery={searchQuery}
                        onClearSearch={() => handleSearch("")}
                        onlyShorts={true}
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
