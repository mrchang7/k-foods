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
    recipe_memo?: string;
    categories: Category[];
}

interface VideoGridProps {
    categories: Category[];
    selectedCategories: number[];
    onRemoveCategory: (id: number) => void;
    excludeVideoIds?: string[];
    searchQuery?: string;
    onClearSearch?: () => void;
}

export default function VideoGrid({ categories, selectedCategories, onRemoveCategory, excludeVideoIds = [], searchQuery = "", onClearSearch }: VideoGridProps) {
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [total, setTotal] = useState(0);
    const observerTarget = useRef<HTMLDivElement>(null);
    const limit = 40;

    // Resolve selected category names
    const activeFilters = categories.filter(c => selectedCategories.includes(c.category_id));

    // Reset videos and page when filters or search change
    useEffect(() => {
        setVideos([]);
        setPage(0);
        setHasMore(true);
    }, [selectedCategories, searchQuery]);

    const loadVideos = useCallback(async () => {
        if (loading || !hasMore) return;
        setLoading(true);

        try {
            const offset = page * limit;
            const apiBase = process.env.NEXT_PUBLIC_API_URL || "";

            let query = `${apiBase}/api/videos?limit=${limit}&offset=${offset}`;

            if (searchQuery) {
                query += `&q=${encodeURIComponent(searchQuery)}`;
            }

            if (selectedCategories.length > 0) {
                selectedCategories.forEach(id => {
                    query += `&category_ids=${id}`;
                });
            }

            if (excludeVideoIds.length > 0) {
                excludeVideoIds.forEach(id => {
                    query += `&exclude_ids=${id}`;
                });
            }

            const res = await fetch(query);
            if (!res.ok) throw new Error("Failed to fetch videos");

            const data = await res.json();

            setVideos((prev) => (page === 0 ? data.videos : [...prev, ...data.videos]));
            setTotal(data.total);

            // If the backend returns 0 items, we've definitively reached the end.
            if (data.videos.length === 0 || data.videos.length < limit) {
                // To be completely safe with deduplication potentially starving out a page,
                // we only rely on length === 0 to actually kill the infinite scroll, 
                // but if it's less than limit initially, we also know we're at the very end.
                setHasMore(data.videos.length === limit);
            }

            setPage((prev) => prev + 1);
        } catch (error) {
            console.error("Error loading videos:", error);
        } finally {
            setLoading(false);
        }
    }, [page, selectedCategories, searchQuery, loading, hasMore, excludeVideoIds]);


    // Intersection Observer for Infinite Scroll
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && !loading && hasMore) {
                    loadVideos();
                }
            },
            { threshold: 0, rootMargin: "600px" }
        );

        if (observerTarget.current) {
            observer.observe(observerTarget.current);
        }

        return () => observer.disconnect();
    }, [loadVideos, loading, hasMore]);


    // Strict Maximum Spread Channel Deduplication: Sliding Window with Deferred Queue
    const deduplicateVideos = (vids: Video[]): Video[] => {
        if (vids.length === 0) return [];

        const result: Video[] = [];
        const WINDOW_SIZE = 12; // Approximate size of a "screen"
        const MAX_PER_WINDOW = 2; // Strict limit: max 2 videos from same channel per screen

        // We will process the incoming fetched videos in order, but defer those that 
        // violate the window constraint until the window shifts enough.
        const pending = [...vids];


        while (pending.length > 0) {
            let madeProgress = false;

            // Try pending queue first
            for (let i = 0; i < pending.length; i++) {
                const v = pending[i];
                const windowStart = Math.max(0, result.length - WINDOW_SIZE);
                let countInWindow = 0;

                for (let j = windowStart; j < result.length; j++) {
                    if (result[j].channel_name === v.channel_name) {
                        countInWindow++;
                    }
                }

                if (countInWindow < MAX_PER_WINDOW) {
                    result.push(v);
                    pending.splice(i, 1);
                    madeProgress = true;
                    break;
                }
            }

            // If we couldn't place any pending video due to strict constraints,
            // we have a "deadlock" for the current window.
            // Move the remaining pending videos to deferred, they will just be appended 
            // once we cannot satisfy the rule.
            if (!madeProgress) {
                break;
            }
        }

        // Any videos strictly violating the rule that couldn't be placed are just pushed to the end.
        // This ensures they are technically still in the list (so infinite scroll math works)
        // but pushed far down.
        return [...result, ...pending];
    };

    const displayableVideos = videos.filter(v => !excludeVideoIds.includes(v.video_id));
    const displayVideos = deduplicateVideos(displayableVideos);

    return (
        <section className="flex-1 min-w-0 p-4 md:p-6 lg:p-8">
            {/* Header with Title & Filters */}
            <div className="flex flex-col mb-5 gap-3 relative -top-3">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 w-full">
                    <div className="flex flex-wrap items-center gap-3 md:gap-4">
                        <h1 className="text-2xl md:text-3xl font-bold text-white">
                            {searchQuery ? (
                                <div className="flex items-baseline gap-2">
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">&ldquo;{searchQuery}&rdquo;</span>
                                    <span className="text-gray-400 font-normal text-xl">관련 요리 레시피</span>
                                </div>
                            ) : (
                                <div className="flex items-end gap-3">
                                    <span>오늘 뭐해 먹지?</span>
                                    {!searchQuery && activeFilters.length === 0 && (
                                        <span className="text-gray-400 text-sm font-normal hidden sm:inline-block mb-1">
                                            당신의 입맛에 딱 맞는 다양한 요리를 찾아보세요 ✨
                                        </span>
                                    )}
                                </div>
                            )}
                        </h1>
                        {searchQuery && onClearSearch && (
                            <button
                                onClick={onClearSearch}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#202020] hover:bg-[#2a2a2a] border border-gray-700 hover:border-red-500 rounded-full text-sm text-gray-300 hover:text-white transition-all shadow-sm"
                            >
                                <span className="text-red-500 font-bold">←</span> 전체 목록 보기
                            </button>
                        )}
                    </div>

                    <div className="flex items-center">
                        <p className="text-gray-400 text-sm whitespace-nowrap">
                            {searchQuery ? "검색 결과" : "추천 레시피"}: <span className="text-white font-semibold">{total.toLocaleString()}</span>개
                        </p>
                    </div>
                </div>

                {/* Active Filter Chips */}
                {activeFilters.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {activeFilters.map(filter => (
                            <button
                                key={filter.category_id}
                                onClick={() => onRemoveCategory(filter.category_id)}
                                className="flex items-center gap-1.5 px-3 py-1 bg-[#202020] border border-gray-700 hover:border-red-500 rounded-full text-sm text-gray-200 transition-colors group"
                            >
                                <span className="text-red-500 font-bold mr-1">Ⓧ</span>
                                {filter.name}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Empty state for search */}
            {searchQuery && !loading && displayVideos.length === 0 && (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <span className="text-5xl mb-4">🍽️</span>
                    <p className="text-xl font-semibold text-white mb-2">
                        &ldquo;{searchQuery}&rdquo; 검색 결과가 없어요
                    </p>
                    <p className="text-gray-500 text-sm">다른 키워드로 검색해 보세요</p>
                </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-6 gap-y-6 mb-12">
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
