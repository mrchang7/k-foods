"use client";

import { useState } from "react";
import Image from "next/image";
import VideoModal from "./VideoModal";

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
    is_vertical?: boolean;
}

export default function VideoCard({ video, rank, layout = 'default', theme = 'default' }: { video: Video, rank?: number, layout?: 'default' | 'compact', theme?: 'default' | 'red' | 'orange' | 'yellow' }) {
    const [imgSrc, setImgSrc] = useState(video.thumbnail_url || "https://via.placeholder.com/320x180");
    const [errorCount, setErrorCount] = useState(0);
    const [showModal, setShowModal] = useState(false);

    // Format view count (e.g., 1500000 -> 150만)
    const formatViews = (views: number) => {
        if (views >= 10000) {
            return `${(views / 10000).toFixed(0)}만회`;
        }
        return `${views.toLocaleString()}회`;
    };

    const handleImageError = () => {
        if (errorCount === 0) {
            if (imgSrc.includes("hqdefault")) {
                setImgSrc(imgSrc.replace("hqdefault", "mqdefault"));
            } else {
                setImgSrc("https://via.placeholder.com/320x180?text=No+Thumbnail");
            }
            setErrorCount(1);
        } else {
            setImgSrc("https://via.placeholder.com/320x180?text=No+Thumbnail");
        }
    };

    const getRankBadgeColors = (t: string) => {
        if (t === 'red') {
            return "bg-gradient-to-br from-rose-400 via-pink-500 to-red-500 text-white border-white/40 shadow-[0_2px_10px_rgba(244,63,94,0.4)]";
        }
        if (t === 'orange') {
            return "bg-gradient-to-br from-amber-300 via-orange-400 to-orange-500 text-white border-white/40 shadow-[0_2px_10px_rgba(246,143,36,0.4)]";
        }
        if (t === 'yellow') {
            return "bg-gradient-to-br from-yellow-100 via-yellow-300 to-amber-400 text-yellow-900 border-white/60 shadow-[0_2px_10px_rgba(252,211,77,0.4)]";
        }
        
        // Default fallback
        return "bg-gradient-to-br from-slate-600 to-slate-800 text-white border-white/20 shadow-md";
    };

    return (
        <>
            {showModal && (
                <VideoModal
                    videoId={video.video_id}
                    title={video.title}
                    channelName={video.channel_name}
                    recipeMemo={video.recipe_memo}
                    onClose={() => setShowModal(false)}
                />
            )}

            <div
                onClick={() => setShowModal(true)}
                className={`group flex rounded-lg overflow-hidden transition-all duration-300 hover:scale-[1.03] hover:bg-[#202020] p-1.5 -m-1.5 cursor-pointer ${
                    layout === 'compact' ? 'flex-row items-center gap-3' : `flex-col gap-1.5 ${video.is_short ? "col-span-1" : "col-span-2 md:col-span-2 lg:col-span-2 xl:col-span-2"}`
                }`}
            >
                <div className={`relative rounded-lg overflow-hidden flex justify-center items-center bg-black flex-shrink-0 ${
                    layout === 'compact' 
                        ? (video.is_short ? "w-[120px] sm:w-[140px] aspect-[9/16]" : "w-52 sm:w-64 aspect-video")
                        : `w-full ${video.is_short ? "aspect-[9/16]" : "aspect-video"}`
                }`}>
                    
                    {/* Main Thumbnail Container */}
                    <div className={`${video.is_vertical && !video.is_short ? "relative h-full aspect-[9/16] overflow-hidden" : "absolute inset-0"}`}>
                        {rank && (
                            <div className={`absolute top-0 left-0 font-black px-3 py-1.5 rounded-br-xl z-20 text-lg shadow-sm border-r border-b flex items-center justify-center min-w-[40px]
                                ${getRankBadgeColors(theme)}
                            `}>
                                {rank}
                            </div>
                        )}
                        <Image
                            src={imgSrc}
                            alt={video.title}
                            fill
                            className={`object-cover z-10 transition-all duration-300 ${
                                video.is_short || video.is_vertical
                                    ? "scale-[1.35] group-hover:scale-[1.4] brightness-90 group-hover:brightness-100" 
                                    : "group-hover:scale-[1.05] group-hover:brightness-110"
                            }`}
                            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                            unoptimized={true}
                            onError={handleImageError}
                        />
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2 z-20">
                        <span className="bg-red-600 text-white text-[10px] sm:text-xs font-bold px-1.5 py-0.5 rounded">▶ 재생</span>
                    </div>
                </div>
                <div className={`flex flex-col px-1 ${layout === 'compact' ? 'flex-1 py-1 justify-center' : ''}`}>
                    <h3 className={`text-white font-medium line-clamp-2 leading-snug group-hover:text-red-400 transition-colors ${layout === 'compact' ? 'text-sm sm:text-base' : 'text-sm'}`}>
                        {video.title}
                    </h3>
                    <div className="flex items-center gap-1.5 text-gray-400 text-[11px] sm:text-xs mt-1">
                        <span className="truncate max-w-[120px]">{video.channel_name}</span>
                        <span className="w-1 h-1 rounded-full bg-gray-600 flex-shrink-0" />
                        <span className="flex-shrink-0">{formatViews(video.view_count)}</span>
                    </div>


                </div>
            </div>
        </>
    );
}
