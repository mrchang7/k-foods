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

    const popularKeywords = ["김치찌개", "불고기", "밑반찬", "된장찌개", "비빔밥", "삼겹살", "떡볶이", "냉면", "갈비"];

    return (
        <>
            {showModal && (
                <VideoModal
                    videoId={HERO_VIDEO_ID}
                    title="치즈 닭갈비 - Honeykki 꿀키"
                    onClose={() => setShowModal(false)}
                />
            )}

            <div className="w-full flex justify-center py-4 px-4 md:px-8 bg-gradient-to-b from-[#141414] to-[#1a1a1a]">
                <div
                    className="w-full max-w-[1600px] relative h-[160px] md:h-[200px] lg:h-[240px] rounded-2xl overflow-hidden shadow-xl group cursor-pointer"
                    onClick={() => setShowModal(true)}
                >
                    {/* Honeykki Cheese Dakgalbi - High Visual Quality */}
                    <Image
                        src="https://img.youtube.com/vi/NwJnm4yQxTc/maxresdefault.jpg"
                        alt="Cheese Dakgalbi"
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-700"
                        priority
                        unoptimized={true}
                    />

                    <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/60 to-transparent opacity-90" />
                    <div className="absolute inset-0 bg-gradient-to-r from-[#141414]/90 via-[#141414]/40 to-transparent opacity-80" />

                    {/* Hero Content */}
                    <div className="absolute inset-0 flex flex-col justify-end p-4 md:p-8 pointer-events-none">
                        <div className="w-full max-w-2xl">
                            <span className="inline-block px-2.5 py-1 mb-2 text-[10px] md:text-xs font-bold text-white bg-red-600 rounded-full tracking-wide shadow-md">
                                ✨ 오늘의 추천 요리
                            </span>
                            <h2 className="text-xl md:text-3xl lg:text-4xl font-extrabold text-white leading-snug mb-2 drop-shadow-[0_4px_4px_rgba(0,0,0,0.8)]">
                                치즈 풍미 폭발! <br />
                                매콤달콤 <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-400">치즈 닭갈비</span> 어때요?
                            </h2>
                            <p className="text-gray-200 text-xs md:text-sm line-clamp-2 max-w-xl font-medium drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] leading-relaxed hidden sm:block">
                                레스토랑 부럽지 않은 화려한 비주얼! 쭉 늘어나는 고소한 치즈와 입맛 돋우는 매콤한 닭갈비의 완벽한 조화를 집에서 즐겨보세요.
                            </p>
                        </div>
                    </div>
                </div>

            </div>

            {/* Search Bar Section — below hero */}
            <div className="w-full bg-gradient-to-b from-[#1a1a1a] to-[#141414] pt-2 pb-0 px-4 flex flex-col items-center gap-3">
                <form
                    onSubmit={handleSearch}
                    className="w-full max-w-xl"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="relative flex items-center group shadow-md rounded-full">
                        <Search className="absolute left-4 w-4 h-4 text-gray-400 group-focus-within:text-red-400 transition-colors pointer-events-none" />
                        <input
                            ref={inputRef}
                            type="text"
                            value={searchInput}
                            placeholder="먹고 싶은 요리를 검색해보세요 (예: 김치찌개, 불고기...)"
                            className="w-full bg-[#202020] border border-gray-700 focus:border-red-500 text-white rounded-full pl-11 pr-24 py-3 text-sm focus:outline-none transition-all placeholder-gray-500 shadow-inner"
                            onChange={(e) => setSearchInput(e.target.value)}
                        />
                        <button
                            type="submit"
                            className="absolute right-1.5 bg-gradient-to-r from-red-600 to-orange-500 hover:from-red-500 hover:to-orange-400 text-white font-bold px-5 py-2 rounded-full transition-all hover:shadow-lg hover:shadow-red-900/30 text-xs"
                        >
                            검색
                        </button>
                    </div>
                </form>

                {/* Popular Keywords */}
                <div className="flex flex-wrap items-center justify-center gap-1.5">
                    <span className="text-gray-500 text-xs mr-1">추천:</span>
                    {popularKeywords.map((kw) => (
                        <button
                            key={kw}
                            onClick={() => handleKeywordClick(kw)}
                            className="px-2.5 py-1 bg-[#202020] hover:bg-[#2a2a2a] border border-gray-700 hover:border-red-500/50 text-gray-300 hover:text-white rounded-full text-xs transition-all"
                        >
                            {kw}
                        </button>
                    ))}
                </div>
            </div>
        </>
    );
}
