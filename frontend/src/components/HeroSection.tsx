"use client";

import { useState } from "react";
import Image from "next/image";
import VideoModal from "./VideoModal";

const HERO_VIDEO_ID = "NwJnm4yQxTc";

export default function HeroSection() {
    const [showModal, setShowModal] = useState(false);

    return (
        <>
            {showModal && (
                <VideoModal
                    videoId={HERO_VIDEO_ID}
                    title="치즈 닭갈비 - Honeykki 꿀키"
                    onClose={() => setShowModal(false)}
                />
            )}

            <div className="w-full flex justify-center py-6 px-4 md:px-8 bg-gradient-to-b from-[#141414] to-[#1a1a1a]">
                <div
                    className="w-full max-w-[1600px] relative aspect-[7/1] md:aspect-[6/1] rounded-2xl overflow-hidden shadow-2xl group cursor-pointer"
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
                    <div className="absolute bottom-0 left-0 p-5 md:p-10 w-full max-w-2xl">
                        <span className="inline-block px-3 py-1 mb-2 md:mb-3 text-xs md:text-sm font-bold text-white bg-red-600 rounded-full tracking-wide shadow-md">
                            ✨ 오늘의 추천 요리
                        </span>
                        <h1 className="text-2xl md:text-4xl lg:text-5xl font-extrabold text-white leading-snug mb-3 md:mb-4 drop-shadow-[0_4px_4px_rgba(0,0,0,0.8)]">
                            치즈 풍미 폭발! <br />
                            매콤달콤 <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-400">치즈 닭갈비</span> 어때요?
                        </h1>
                        <p className="text-gray-100 text-sm md:text-base lg:text-lg mb-5 md:mb-6 line-clamp-2 max-w-xl font-medium drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] leading-relaxed">
                            레스토랑 부럽지 않은 화려한 비주얼! 쭉 늘어나는 고소한 치즈와 입맛 돋우는 매콤한 닭갈비의 완벽한 조화를 집에서 즐겨보세요.
                        </p>
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowModal(true); }}
                            className="inline-flex items-center gap-2 bg-white text-black px-5 py-2.5 md:px-7 md:py-3.5 rounded-full font-bold hover:bg-gray-100 transition-colors shadow-lg hover:scale-105 transform duration-200"
                        >
                            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                                <path d="M8 5v14l11-7z" />
                            </svg>
                            지금 바로 시청하기
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
