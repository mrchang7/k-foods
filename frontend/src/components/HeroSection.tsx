"use client";

import Image from "next/image";

export default function HeroSection() {
    return (
        <div className="w-full flex justify-center py-6 px-4 md:px-8 bg-gradient-to-b from-[#141414] to-[#1a1a1a]">
            <div className="w-full max-w-[1600px] relative aspect-[21/5] md:aspect-[24/6] rounded-2xl overflow-hidden shadow-2xl group cursor-pointer">
                {/* Honeykki Cheese Dakgalbi - High Visual Quality */}
                <Image
                    src="https://img.youtube.com/vi/NwJnm4yQxTc/maxresdefault.jpg"
                    alt="Cheese Dakgalbi"
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-700"
                    priority
                    unoptimized={true}
                />

                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/40 to-transparent opacity-90" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-transparent to-transparent opacity-60" />

                {/* Hero Content */}
                <div className="absolute bottom-0 left-0 p-8 md:p-12 w-full max-w-2xl">
                    <span className="inline-block px-3 py-1 mb-4 text-xs font-bold text-white bg-red-600 rounded-sm tracking-wider uppercase">
                        CHEF'S SIGNATURE
                    </span>
                    <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-4 drop-shadow-lg">
                        입안 가득 행복한 <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">치즈 닭갈비</span>
                    </h1>
                    <p className="text-gray-300 text-base md:text-lg mb-6 line-clamp-2 max-w-xl">
                        쭉쭉 늘어나는 고소한 치즈와 매콤한 닭갈비의 환상적인 만남. 꿀키의 감성 레시피로 만나보세요.
                    </p>
                    <a
                        href="https://www.youtube.com/watch?v=NwJnm4yQxTc"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 rounded font-bold hover:bg-gray-200 transition-colors"
                    >
                        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                        </svg>
                        지금 바로 시청하기
                    </a>
                </div>
            </div>
        </div>
    );
}
