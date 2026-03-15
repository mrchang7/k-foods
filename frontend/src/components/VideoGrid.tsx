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
    is_short?: boolean;
}

interface VideoGridProps {
    categories: Category[];
    selectedCategories: number[];
    onRemoveCategory: (id: number) => void;
    excludeVideoIds?: string[];
    searchQuery?: string;
    onClearSearch?: () => void;
    showShorts?: boolean;
    onlyShorts?: boolean;
}

export default function VideoGrid({ categories, selectedCategories, onRemoveCategory, excludeVideoIds = [], searchQuery = "", onClearSearch, showShorts = true, onlyShorts = false }: VideoGridProps) {
    const [videos, setVideos] = useState<Video[]>([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [total, setTotal] = useState(0);
    const observerTarget = useRef<HTMLDivElement>(null);
    const limit = 40;
    
    // Generate a random seed once per component mount to shuffle the feed slightly
    // but keep pagination completely stable.
    const [sessionSeed] = useState(() => Math.floor(Math.random() * 1000) + 1);

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

            let query = `${apiBase}/api/videos?limit=${limit}&offset=${offset}&seed=${sessionSeed}`;

            if (onlyShorts) {
                query += `&only_shorts=true`;
            }

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

    // Failsafe: Catch race conditions where `searchQuery` resets the grid to empty, 
    // but the intersection observer callback misses it because the previous keypress fetch was still `loading`.
    useEffect(() => {
        if (!loading && hasMore && videos.length === 0 && page === 0) {
            loadVideos();
        }
    }, [loading, hasMore, videos.length, page, loadVideos]);


    // Sliding Window Interleaver to strictly space out same-channel videos
    const deduplicateVideos = (vids: Video[]): Video[] => {
        if (vids.length === 0) return [];

        const result: Video[] = [];
        const remaining = [...vids];
        
        // Define how many videos constitute a "screen"
        const W = onlyShorts ? 21 : 12; 
        const MAX_COUNT = 2; // Max 2 from the same channel in any window of size W
        
        while (remaining.length > 0) {
            let foundValid = false;
            
            for (let i = 0; i < remaining.length; i++) {
                const candidate = remaining[i];
                
                // 1. Check window constraint
                // We check the last (W - 1) elements to see if candidate violates MAX_COUNT
                const windowStart = Math.max(0, result.length - (W - 1));
                let count = 0;
                for (let j = windowStart; j < result.length; j++) {
                    if (result[j].channel_name === candidate.channel_name) {
                        count++;
                    }
                }
                
                if (count < MAX_COUNT) {
                    // 2. Strict Adjacency Constraint: Don't allow immediately consecutive videos from same channel if possible
                    const isAdjacent = result.length > 0 && result[result.length - 1].channel_name === candidate.channel_name;
                    
                    if (!isAdjacent) {
                        result.push(candidate);
                        remaining.splice(i, 1);
                        foundValid = true;
                        break;
                    }
                }
            }
            
            // If strictly separated videos cannot be found (e.g. the remaining list is dominated by one channel)
            if (!foundValid) {
                // Relax constraints: Just try to break adjacency at least, ignoring the window limit.
                let fallbackIndex = 0;
                for (let i = 0; i < remaining.length; i++) {
                    if (result.length === 0 || result[result.length - 1].channel_name !== remaining[i].channel_name) {
                        fallbackIndex = i;
                        break;
                    }
                }
                result.push(remaining[fallbackIndex]);
                remaining.splice(fallbackIndex, 1);
            }
        }

        return result;
    };

    const displayableVideos = videos.filter(v => {
        if (excludeVideoIds.includes(v.video_id)) return false;
        return true;
    });

    // If searching, we don't want to deduplicate because search results are usually small
    // and highly specific. Deduplication might hide the exact video the user is looking for.
    const displayVideos = searchQuery ? displayableVideos : deduplicateVideos(displayableVideos);

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
                                    {!searchQuery && activeFilters.length === 0 && (
                                        <h2 className="text-2xl font-bold flex items-center gap-2 text-white">
                                            {onlyShorts ? (
                                                <><span className="text-red-500">📱</span> 전체 쇼츠</>
                                            ) : (
                                                <><span className="text-red-500">🍲</span> 주메뉴 레시피</>
                                            )}
                                        </h2>
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

            <div className={`grid gap-x-4 gap-y-6 mb-12 ${onlyShorts
                    ? "grid-cols-3 sm:grid-cols-4 md:grid-cols-7 lg:grid-cols-7 xl:grid-cols-7 2xl:grid-cols-7"
                    : "grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8"
                }`}>
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
