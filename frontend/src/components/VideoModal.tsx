"use client";

import { useEffect, useRef, useState } from "react";

interface VideoModalProps {
    videoId: string;
    title: string;
    channelName?: string;
    recipeMemo?: string;
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

export default function VideoModal({ videoId, title, channelName, recipeMemo, onClose }: VideoModalProps) {
    const playerContainerRef = useRef<HTMLDivElement>(null);
    const playerRef = useRef<any>(null);
    const [showRecipe, setShowRecipe] = useState(false);

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

            playerRef.current = new window.YT.Player(playerContainerRef.current, {
                videoId,
                playerVars: {
                    autoplay: 1,
                    rel: 0,
                    modestbranding: 1,
                },
                events: {
                    onReady: (e: any) => {
                        playerRef.current = e.target;
                    },
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

    const handleTimestampClick = (timeStr: string) => {
        if (!playerRef.current || typeof playerRef.current.seekTo !== "function") return;
        const match = timeStr.match(/(\d{1,2}):(\d{2})/);
        if (match) {
            const mins = parseInt(match[1], 10);
            const secs = parseInt(match[2], 10);
            playerRef.current.seekTo(mins * 60 + secs, true);
            if (typeof playerRef.current.playVideo === "function") {
                playerRef.current.playVideo();
            }
        }
    };

    const renderRecipeText = (text: string) => {
        if (!text) return null;

        const lines = text.split("\n");
        return lines.map((line, i) => {
            const trimmed = line.trim();
            if (!trimmed) return <div key={i} className="h-3" />; // Empty spaces

            const isTitle = trimmed.includes("👨‍🍳");
            const isHeader = trimmed.includes("📍");

            let className = "text-gray-300 ml-1 mb-2 leading-relaxed text-[15px]";
            if (isTitle) {
                className = "font-bold text-white text-lg mb-5 border-b border-gray-700 pb-3";
            } else if (isHeader) {
                className = "font-semibold text-red-400 mt-6 mb-3 text-base flex items-center";
            }

            const regex = /(\[\d{1,2}:\d{2}\]|\b\d{1,2}:\d{2}\b)/g;
            const parts = trimmed.split(regex);

            return (
                <div key={i} className={className}>
                    {parts.map((part, j) => {
                        if (regex.test(part)) {
                            return (
                                <button
                                    key={j}
                                    onClick={(e) => {
                                        e.preventDefault();
                                        handleTimestampClick(part);
                                    }}
                                    className="underline hover:text-white transition-colors cursor-pointer"
                                    title="이 시간으로 영상 이동"
                                >
                                    {part}
                                </button>
                            );
                        }
                        return <span key={j}>{part}</span>;
                    })}
                </div>
            );
        });
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="relative w-[80vw] h-[80vh] rounded-xl overflow-hidden shadow-2xl flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Title bar: channel left | title center | recipe & close right */}
                <div className="relative flex items-center bg-black/90 px-4 py-2 flex-shrink-0 h-14">
                    {/* Channel name — left */}
                    {channelName && (
                        <span className="text-gray-400 text-sm font-normal truncate max-w-[20%]">{channelName}</span>
                    )}
                    {/* Title — absolute center */}
                    <span className="absolute left-1/2 -translate-x-1/2 text-white text-base font-semibold text-center line-clamp-1 max-w-[40%]">
                        {title}
                    </span>
                    {/* Actions — right */}
                    <div className="ml-auto flex items-center gap-3">
                        {recipeMemo && (
                            <button
                                onClick={() => setShowRecipe(!showRecipe)}
                                className={`px-4 py-1.5 rounded-full text-sm font-bold transition-all shadow-md ${showRecipe
                                    ? "bg-red-600 text-white"
                                    : "bg-[#252525] hover:bg-[#353535] text-red-400 border border-gray-700 hover:border-red-500"}`}
                            >
                                {showRecipe ? "레시피 닫기" : "📋 레시피"}
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="bg-black/70 hover:bg-neutral-800 border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white rounded-full w-10 h-10 flex items-center justify-center transition-colors text-2xl font-light shadow-lg flex-shrink-0"
                            aria-label="Close"
                        >
                            ×
                        </button>
                    </div>
                </div>

                <div className="flex-1 flex overflow-hidden w-full">
                    {/* YouTube player container */}
                    <div className="flex flex-col h-full bg-black transition-all duration-500 ease-in-out" style={{ width: showRecipe ? "66.666%" : "100%" }}>
                        <div ref={playerContainerRef} className="flex-1 w-full" />
                        {/* "Open on YouTube" fallback link */}
                        <a
                            href={`https://www.youtube.com/watch?v=${videoId}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block text-center text-xs text-gray-400 hover:text-white bg-black/80 py-1.5 transition-colors border-t border-gray-800"
                            onClick={(e) => e.stopPropagation()}
                        >
                            ▶ YouTube에서 보기
                        </a>
                    </div>

                    {/* Recipe Panel */}
                    {showRecipe && recipeMemo && (
                        <div className="w-1/3 h-full bg-[#141414] border-l border-gray-800 p-6 overflow-y-auto text-gray-200">
                            <h3 className="text-xl font-bold text-white mb-6 border-b border-gray-800 pb-3 flex justify-between items-center">
                                <span>📋 레시피 메모</span>
                                <span className="text-xs font-normal text-gray-500 bg-gray-900 px-2 py-1 rounded hidden lg:block">AI 자동 요약</span>
                            </h3>

                            <div className="flex flex-col">
                                {renderRecipeText(recipeMemo)}
                            </div>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
