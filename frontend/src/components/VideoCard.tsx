"use client";

import { useState } from "react";
import Image from "next/image";

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

export default function VideoCard({ video }: { video: Video }) {
    const [imgSrc, setImgSrc] = useState(video.thumbnail_url || "https://via.placeholder.com/320x180");
    const [errorCount, setErrorCount] = useState(0);

    // Format view count (e.g., 1500000 -> 150만)
    const formatViews = (views: number) => {
        if (views >= 10000) {
            return `${(views / 10000).toFixed(0)}만회`;
        }
        return `${views.toLocaleString()}회`;
    };

    const handleImageError = () => {
        if (errorCount === 0) {
            // Try mqdefault if hqdefault fails
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

    return (
        <a
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex flex-col gap-3 rounded-lg overflow-hidden transition-all duration-300 hover:scale-105 hover:bg-[#202020] p-2 -m-2"
        >
            <div className="relative aspect-video w-full rounded-lg overflow-hidden bg-gray-800">
                <Image
                    src={imgSrc}
                    alt={video.title}
                    fill
                    className="object-cover group-hover:brightness-110 transition-all"
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    unoptimized={true}
                    onError={handleImageError}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                    <span className="bg-red-600 text-white text-xs font-bold px-2 py-1 rounded">▶ 재생</span>
                </div>
            </div>
            <div className="flex flex-col px-1">
                <h3 className="text-white font-semibold text-base line-clamp-2 leading-tight group-hover:text-red-400 transition-colors">
                    {video.title}
                </h3>
                <div className="flex items-center gap-2 text-gray-400 text-xs mt-1">
                    <span>{video.channel_name}</span>
                    <span className="w-1 h-1 rounded-full bg-gray-600" />
                    <span>{formatViews(video.view_count)}</span>
                </div>

                {/* Category Badges */}
                <div className="flex flex-wrap gap-1 mt-2">
                    {video.categories.map((cat) => (
                        <span
                            key={cat.category_id}
                            className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-gray-800 text-gray-300 border border-gray-700"
                        >
                            {cat.name}
                        </span>
                    ))}
                </div>
            </div>
        </a>
    );
}
