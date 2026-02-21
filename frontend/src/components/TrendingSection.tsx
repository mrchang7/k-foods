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
    categories: Category[];
}

interface TrendingSectionProps {
    onVideosLoaded?: (videoIds: string[]) => void;
}

export default function TrendingSection({ onVideosLoaded }: TrendingSectionProps) {
    const [period, setPeriod] = useState<"daily" | "weekly" | "monthly">("weekly");
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);
    const [atStart, setAtStart] = useState(true);
    const [atEnd, setAtEnd] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchTrending = async () => {
            setLoading(true);
            try {
                const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://10.0.0.241:8000";
                const response = await fetch(`${baseUrl}/api/videos/trending?period=${period}&limit=10`);
                if (response.ok) {
                    const data: Video[] = await response.json();
                    setVideos(data);
                    if (onVideosLoaded) {
                        onVideosLoaded(data.map(v => v.video_id));
                    }
                }
            } catch (error) {
                console.error("Failed to fetch trending videos:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTrending();
    }, [period, onVideosLoaded]);

    const scroll = (dir: "left" | "right") => {
        if (scrollRef.current) {
            scrollRef.current.scrollBy({ left: dir === "right" ? 320 : -320, behavior: "smooth" });
        }
    };

    const handleScroll = () => {
        if (!scrollRef.current) return;
        const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
        setAtStart(scrollLeft <= 0);
        setAtEnd(scrollLeft + clientWidth >= scrollWidth - 4);
    };

    return (
        <section className="w-full max-w-[1600px] mx-auto px-4 md:px-8 py-10">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between mb-6 gap-4 border-b border-gray-800 pb-4">
                <div className="flex items-center gap-3">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <span className="text-red-500">🔥</span> 실시간 인기 급상승
                    </h2>
                    <span className="text-gray-400 text-sm hidden sm:inline-block">
                        요즘 가장 핫한 레시피를 만나보세요
                    </span>
                </div>

                {/* Period Tabs */}
                <div className="flex bg-[#1a1a1a] rounded-lg p-1">
                    {(["daily", "weekly", "monthly"] as const).map(p => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${period === p ? "bg-red-600 text-white shadow-sm" : "text-gray-400 hover:text-white"
                                }`}
                        >
                            {p === "daily" ? "일간" : p === "weekly" ? "주간" : "월간"}
                        </button>
                    ))}
                </div>
            </div>

            {/* Horizontal Scroll Container */}
            <div className="relative px-14">
                {!atStart && (
                    <button
                        onClick={() => scroll("left")}
                        className="absolute left-0 top-[45%] -translate-y-1/2 z-10 bg-black/70 hover:bg-red-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg transition-colors text-4xl font-light"
                        aria-label="Scroll left"
                    >
                        ‹
                    </button>
                )}

                {loading ? (
                    <div className="w-full flex justify-center items-center py-16">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
                    </div>
                ) : videos.length > 0 ? (
                    <div
                        ref={scrollRef}
                        onScroll={handleScroll}
                        className="flex gap-4 overflow-x-auto scroll-smooth pb-3"
                        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
                    >
                        {videos.map((video, index) => (
                            <div
                                key={`trending-${video.video_id}-${index}`}
                                className="flex-none w-[220px]"
                            >
                                <VideoCard video={video} />
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="w-full flex justify-center items-center py-16 text-gray-500">
                        해당 기간의 인기 영상이 없습니다.
                    </div>
                )}

                {!atEnd && (
                    <button
                        onClick={() => scroll("right")}
                        className="absolute right-0 top-[45%] -translate-y-1/2 z-10 bg-black/70 hover:bg-red-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg transition-colors text-4xl font-light"
                        aria-label="Scroll right"
                    >
                        ›
                    </button>
                )}
            </div>
        </section>
    );
}
