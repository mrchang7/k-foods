"use client";

import Image from "next/image";

export default function HeroSection() {
    return (
        <div className="w-full flex justify-center py-6 px-4 md:px-8 bg-gradient-to-b from-[#141414] to-[#1a1a1a]">
            <div className="w-full max-w-[1600px] relative aspect-[21/9] md:aspect-[24/7] rounded-2xl overflow-hidden shadow-2xl group cursor-pointer">
                {/* Placeholder Hero Image */}
                <Image
                    src="https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?q=80&w=2000&auto=format&fit=crop"
                    alt="Hero Banner"
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-700"
                    priority
                />

                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/50 to-transparent opacity-90" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-transparent to-transparent opacity-70" />

                {/* Hero Content */}
                <div className="absolute bottom-0 left-0 p-8 md:p-12 w-full max-w-2xl">
                    <span className="inline-block px-3 py-1 mb-4 text-xs font-bold text-white bg-red-600 rounded-sm tracking-wider uppercase">
                        TRENDING TODAY
                    </span>
                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-tight mb-4 drop-shadow-lg">
                        지금 가장 핫한 <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">겨울 방어</span> 맛집 레시피
                    </h1>
                    <p className="text-gray-300 text-lg md:text-xl mb-6 line-clamp-2 max-w-xl">
                        제철 맞은 대방어, 집에서도 전문점처럼 즐기는 셰프들의 꿀팁 대공개!
                    </p>
                    <button className="flex items-center gap-2 bg-white text-black px-6 py-3 rounded font-bold hover:bg-gray-200 transition-colors">
                        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                        </svg>
                        재생하기
                    </button>
                </div>
            </div>
        </div>
    );
}
