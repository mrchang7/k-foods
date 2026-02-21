"use client";

import { useEffect, useRef } from "react";

interface VideoModalProps {
    videoId: string;
    title: string;
    channelName?: string;
    onClose: () => void;
}

// Extend window for YouTube IFrame API
declare global {
    interface Window {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        YT: any;
        onYouTubeIframeAPIReady: () => void;
    }
}

export default function VideoModal({ videoId, title, channelName, onClose }: VideoModalProps) {
    const playerContainerRef = useRef<HTMLDivElement>(null);

    // Close on Escape key
    useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    // Load YouTube IFrame API and initialize player with error fallback
    useEffect(() => {
        const initPlayer = () => {
            if (!playerContainerRef.current) return;

            new window.YT.Player(playerContainerRef.current, {
                videoId,
                playerVars: {
                    autoplay: 1,
                    rel: 0,
                    modestbranding: 1,
                },
                events: {
                    onError: (e: { data: number }) => {
                        // Error 101 or 150 = embedding blocked by video owner
                        if (e.data === 101 || e.data === 150 || e.data === 100) {
                            // Fall back to opening in YouTube with autoplay
                            window.open(
                                `https://www.youtube.com/watch?v=${videoId}&autoplay=1`,
                                "_blank",
                                "noopener,noreferrer"
                            );
                            onClose();
                        }
                    },
                },
            });
        };

        if (window.YT && window.YT.Player) {
            // API already loaded
            initPlayer();
        } else {
            // Load the API script
            const existing = document.getElementById("yt-iframe-api");
            if (!existing) {
                const tag = document.createElement("script");
                tag.id = "yt-iframe-api";
                tag.src = "https://www.youtube.com/iframe_api";
                document.head.appendChild(tag);
            }
            // Queue init for when API is ready
            const prev = window.onYouTubeIframeAPIReady;
            window.onYouTubeIframeAPIReady = () => {
                if (prev) prev();
                initPlayer();
            };
        }
    }, [videoId, onClose]);

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="relative w-[80vw] h-[80vh] rounded-xl overflow-hidden shadow-2xl flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Title bar: channel left | title center | close right */}
                <div className="relative flex items-center bg-black/90 px-4 py-2 flex-shrink-0 h-14">
                    {/* Channel name — left */}
                    {channelName && (
                        <span className="text-gray-400 text-sm font-normal truncate max-w-[30%]">{channelName}</span>
                    )}
                    {/* Title — absolute center */}
                    <span className="absolute left-1/2 -translate-x-1/2 text-white text-base font-semibold text-center line-clamp-1 max-w-[50%]">
                        {title}
                    </span>
                    {/* Close button — right */}
                    <button
                        onClick={onClose}
                        className="ml-auto bg-black/70 hover:bg-red-600 text-white rounded-full w-12 h-12 flex items-center justify-center transition-colors text-3xl font-bold shadow-lg flex-shrink-0"
                        aria-label="Close"
                    >
                        ×
                    </button>
                </div>

                {/* YouTube player container */}
                <div ref={playerContainerRef} className="flex-1 w-full" />

                {/* "Open on YouTube" fallback link */}
                <a
                    href={`https://www.youtube.com/watch?v=${videoId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-center text-xs text-gray-400 hover:text-white bg-black/80 py-1.5 transition-colors"
                    onClick={(e) => e.stopPropagation()}
                >
                    ▶ YouTube에서 보기
                </a>
            </div>
        </div>
    );
}
