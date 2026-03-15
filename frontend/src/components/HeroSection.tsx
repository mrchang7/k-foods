"use client";

import { useState, useRef } from "react";
import Image from "next/image";
import VideoModal from "./VideoModal";
import { Search } from "lucide-react";

const HERO_VIDEO_ID = "NwJnm4yQxTc";

interface HeroSectionProps {
    onSearch: (q: string) => void;
}

export default function HeroSection({ onSearch }: HeroSectionProps) {
    const [showModal, setShowModal] = useState(false);
    const [searchInput, setSearchInput] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch(searchInput.trim());
    };

    const handleKeywordClick = (keyword: string) => {
        setSearchInput(keyword);
        onSearch(keyword);
    };

    const popularKeywords = ["김치찌개", "불고기", "밑반찬", "된장찌개", "비빔밥", "삼겹살", "떡볶이", "냉면", "갈비", "제육볶음", "계란말이", "닭볶음탕"];

    return (
        <>
            {showModal && (
                <VideoModal
                    videoId={HERO_VIDEO_ID}
                    title="치즈 닭갈비 - Honeykki 꿀키"
                    onClose={() => setShowModal(false)}
                />
            )}

            {/* Search Bar Section — below hero */}
            <div className="w-full bg-gradient-to-b from-[#1a1a1a] to-[#141414] py-5 px-4 flex flex-col items-center gap-3">
                <form
                    onSubmit={handleSearch}
                    className="w-full max-w-2xl"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="relative flex items-center group shadow-xl rounded-full">
                        <Search className="absolute left-5 w-5 h-5 text-gray-400 group-focus-within:text-red-400 transition-colors pointer-events-none" />
                        <input
                            ref={inputRef}
                            type="text"
                            value={searchInput}
                            placeholder="먹고 싶은 요리를 검색해보세요 (예: 김치찌개, 불고기...)"
                            className="w-full bg-[#202020]/80 backdrop-blur-sm border-2 border-gray-700/50 focus:border-red-500/80 text-white rounded-full pl-14 pr-32 py-3 text-base focus:outline-none transition-all placeholder-gray-500 shadow-inner"
                            onChange={(e) => setSearchInput(e.target.value)}
                        />
                        <button
                            type="submit"
                            className="absolute right-1.5 bg-gradient-to-r from-red-600 to-orange-500 hover:from-red-500 hover:to-orange-400 text-white font-bold px-7 py-2 rounded-full transition-all hover:shadow-lg hover:shadow-red-900/30 text-sm"
                        >
                            검색
                        </button>
                    </div>
                </form>

                {/* Popular Keywords */}
                <div className="flex flex-wrap items-center justify-center gap-1.5 mt-0 max-w-4xl">
                    <span className="text-gray-400 text-xs mr-1 font-medium">추천 검색어:</span>
                    {popularKeywords.map((kw) => (
                        <button
                            key={kw}
                            onClick={() => handleKeywordClick(kw)}
                            className="px-3 py-1 bg-[#202020]/60 hover:bg-[#2a2a2a] border border-gray-700/50 hover:border-red-500/50 text-gray-300 hover:text-white rounded-full text-xs transition-all shadow-sm"
                        >
                            {kw}
                        </button>
                    ))}
                </div>
            </div>
        </>
    );
}
