"use client";

import { useState, useEffect, useRef } from "react";
import VideoCard from "./VideoCard";

interface Category {
    category_id: number;
    name: string;
    category_type: string;
}

interface Video {
    video_id: string;
    title: string;
    thumbnail_url: string;
    channel_name: string;
    view_count: number;
    published_at: string;
    url: string;
    recipe_memo?: string;
    categories: Category[];
    is_short?: boolean;
}

export default function ShortsCarousel() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [atStart, setAtStart] = useState(true);
    const [atEnd, setAtEnd] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchShorts = async () => {
            setLoading(true);
            try {
                const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
                // Note: The backend needs to support a way to fetch only shorts,
                // or we just fetch a batch and filter client-side for now, 
                // but let's assume we can fetch them via a dedicated endpoint or we just filter.
                // Let's use the trending endpoint as a base and then query for shorts
                const response = await fetch(`${baseUrl}/api/videos?limit=100`);
                if (response.ok) {
                    const data = await response.json();
                    const shorts = data.videos.filter((v: Video) => v.is_short).slice(0, 15); // Take top 15 shorts
                    setVideos(shorts);
                }
            } catch (error) {
                console.error("Failed to fetch shorts videos:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchShorts();
    }, []);

    const scroll = (dir: "left" | "right") => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({ left: dir === "right" ? 400 : -400, behavior: "smooth" });
        }
    };

    const handleScroll = () => {
        if (!scrollRef.current) return;
        const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
        setAtStart(scrollLeft <= 0);
        setAtEnd(scrollLeft + clientWidth >= scrollWidth - 4);
    };

    if (loading || videos.length === 0) return null;

    return (
        <section id="shorts-section" className="w-full bg-[#1a1a1a] py-8 border-t border-gray-800">
            <div className="max-w-[1600px] mx-auto px-4 md:px-8">
                <div className="flex items-center gap-3 mb-6">
                    <h2 className="text-2xl font-bold flex items-center gap-2 text-white">
                        <span className="text-red-500">📱</span> 1분 뚝딱! 쇼츠 레시피
                    </h2>
                    <span className="text-gray-400 text-sm hidden sm:inline-block font-medium">
                        짧지만 강력한 레시피 모음
                    </span>
                </div>

                <div className="relative group/carousel">
                    {!atStart && (
                        <button
                            onClick={() => scroll("left")}
                            className="absolute left-[-1rem] top-1/2 -translate-y-1/2 z-10 bg-black/80 hover:bg-red-600 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-[0_0_15px_rgba(0,0,0,0.5)] transition-all text-3xl font-light opacity-0 group-hover/carousel:opacity-100"
                            aria-label="Scroll left"
                        >
                            ‹
                        </button>
                    )}

                    <div
                        ref={scrollRef}
                        onScroll={handleScroll}
                        className="flex gap-4 overflow-x-auto scroll-smooth pb-4 px-1"
                        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
                    >
                        {videos.map((video, index) => (
                            <div
                                key={`short-${video.video_id}-${index}`}
                                className="flex-none w-[160px] md:w-[200px]"
                            >
                                <VideoCard video={video} />
                            </div>
                        ))}
                    </div>

                    {!atEnd && (
                        <button
                            onClick={() => scroll("right")}
                            className="absolute right-[-1rem] top-1/2 -translate-y-1/2 z-10 bg-black/80 hover:bg-red-600 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-[0_0_15px_rgba(0,0,0,0.5)] transition-all text-3xl font-light opacity-0 group-hover/carousel:opacity-100"
                            aria-label="Scroll right"
                        >
                            ›
                        </button>
                    )}
                </div>
            </div>
        </section>
    );
}
