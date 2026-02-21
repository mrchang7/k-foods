"use client";

import { useState, useEffect, useCallback, useRef } from "react";
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

interface VideoGridProps {
    categories: Category[];
    selectedCategories: number[];
    onRemoveCategory: (id: number) => void;
}

export default function VideoGrid({ categories, selectedCategories, onRemoveCategory }: VideoGridProps) {
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [total, setTotal] = useState(0);
    const observerTarget = useRef<HTMLDivElement>(null);
    const limit = 20;

    // Resolve selected category names
    const activeFilters = categories.filter(c => selectedCategories.includes(c.category_id));

    // Reset videos and page when filters change
    useEffect(() => {
        setVideos([]);
        setPage(0);
        setHasMore(true);
    }, [selectedCategories]);

    const loadVideos = useCallback(async () => {
        if (loading || !hasMore) return;
        setLoading(true);

        try {
            const offset = page * limit;
            const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

            let query = `${apiBase}/api/videos?limit=${limit}&offset=${offset}`;

            if (selectedCategories.length > 0) {
                selectedCategories.forEach(id => {
                    query += `&category_ids=${id}`;
                });
            }

            const res = await fetch(query);
            if (!res.ok) throw new Error("Failed to fetch videos");

            const data = await res.json();

            setVideos((prev) => (page === 0 ? data.videos : [...prev, ...data.videos]));
            setTotal(data.total);

            // If we received fewer items than requested, we've reached the end
            if (data.videos.length < limit) {
                setHasMore(false);
            } else {
                setPage((prev) => prev + 1);
            }
        } catch (error) {
            console.error("Error loading videos:", error);
        } finally {
            setLoading(false);
        }
    }, [page, selectedCategories, loading, hasMore]);


    // Intersection Observer for Infinite Scroll
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && !loading && hasMore) {
                    loadVideos();
                }
            },
            { threshold: 1.0 }
        );

        if (observerTarget.current) {
            observer.observe(observerTarget.current);
        }

        return () => observer.disconnect();
    }, [loadVideos, loading, hasMore]);


    // Channel Deduplication Logic: Prevent adjacent videos from the same channel
    const deduplicateVideos = (vids: Video[]): Video[] => {
        if (vids.length === 0) return [];
        const result: Video[] = [vids[0]];
        const remaining = vids.slice(1);

        let i = 0;
        while (remaining.length > 0 && i < 100) { // Limit iterations to avoid infinite loop
            let found = false;
            for (let j = 0; j < remaining.length; j++) {
                if (remaining[j].channel_name !== result[result.length - 1].channel_name) {
                    result.push(remaining.splice(j, 1)[0]);
                    found = true;
                    break;
                }
            }
            if (!found) {
                // If no different channel found, just push the first remaining
                result.push(remaining.splice(0, 1)[0]);
            }
            i++;
        }
        return [...result, ...remaining];
    };

    const displayVideos = deduplicateVideos(videos);

    return (
        <section className="flex-1 min-w-0">
            {/* Header with Title & Filters */}
            <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-white mb-4">
                        이런 요리 어때요?
                    </h1>
                    {/* Active Filter Chips */}
                    <div className="flex flex-wrap gap-2">
                        {activeFilters.length > 0 ? (
                            activeFilters.map(filter => (
                                <button
                                    key={filter.category_id}
                                    onClick={() => onRemoveCategory(filter.category_id)}
                                    className="flex items-center gap-1.5 px-3 py-1 bg-[#202020] border border-gray-700 hover:border-red-500 rounded-full text-sm text-gray-200 transition-colors group"
                                >
                                    <span className="text-red-500 font-bold mr-1">Ⓧ</span>
                                    {filter.name}
                                </button>
                            ))
                        ) : (
                            <span className="text-gray-500 text-sm">다양한 요리를 만나보세요</span>
                        )}
                    </div>
                </div>
                <p className="text-gray-400 text-sm whitespace-nowrap">
                    추천 레시피: <span className="text-white font-semibold">{total.toLocaleString()}</span>개
                </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-6 gap-y-10 mb-12">
                {displayVideos.map((video, index) => (
                    <VideoCard key={`${video.video_id}-${index}`} video={video} />
                ))}
            </div>{loading && (
                <div className="w-full flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
                </div>
            )}

            {/* Target element for Intersection Observer */}
            <div ref={observerTarget} className="h-10 w-full" />
        </section>
    );
}
