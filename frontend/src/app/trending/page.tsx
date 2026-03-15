"use client";

import { useState, useEffect, useCallback } from "react";
import Header from "@/components/Header";
import TrendingSection from "@/components/TrendingSection";
import { Category } from "@/components/Sidebar";

export default function TrendingPage() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [, setIsMobileMenuOpen] = useState(false);

    // Fetch categories on mount for the Header
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

    const handleSearch = useCallback((q: string) => {
        // If the user searches from the header, we can redirect them back to the main page
        // Alternatively, they could stay on this page, but redirecting to home makes more sense for search results
        if (q.trim() !== "") {
            window.location.href = `/?search=${encodeURIComponent(q)}`;
        }
    }, []);

    return (
        <div className="bg-[#141414] min-h-screen text-white font-sans flex flex-col">
            <Header
                categories={categories}
                onMenuClick={() => setIsMobileMenuOpen(true)}
                onSearch={handleSearch}
            />

            <main className="flex-1 w-full mt-6 max-w-[1600px] mx-auto px-4 md:px-8">
                {/* Displaying Daily, Weekly, and Monthly Trending Sections in 3 columns */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 pb-12">
                    <TrendingSection
                        fixedPeriod="daily"
                        title={<><span className="text-red-500">🏆</span> 일간 베스트</>}
                        subtitle="오늘 하루 가장 핫한 레시피"
                        compactLayout={true}
                        theme="red"
                    />
                    <TrendingSection
                        fixedPeriod="weekly"
                        title={<><span className="text-orange-500">🏆</span> 주간 베스트</>}
                        subtitle="이번 주 제일 많이 본 레시피"
                        compactLayout={true}
                        theme="orange"
                    />
                    <TrendingSection
                        fixedPeriod="monthly"
                        title={<><span className="text-yellow-500">🏆</span> 월간 베스트</>}
                        subtitle="이번 달 꾸준히 사랑받은 레시피"
                        compactLayout={true}
                        theme="yellow"
                    />
                </div>
            </main>
        </div>
    );
}
