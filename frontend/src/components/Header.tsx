"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Category } from "./Sidebar";
import { Search, Menu, X } from "lucide-react";

interface HeaderProps {
    categories: Category[];
    onMenuClick: () => void;
    onSearch: (q: string) => void;
}

export default function Header({ categories, onMenuClick, onSearch }: HeaderProps) {
    const [hoveredMenu, setHoveredMenu] = useState<number | null>(null);
    const [inputValue, setInputValue] = useState("");
    const [isMobileSearchOpen, setIsMobileSearchOpen] = useState(false);
    const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const desktopInputRef = useRef<HTMLInputElement>(null);
    const mobileInputRef = useRef<HTMLInputElement>(null);

    // Group root categories (대분류)
    const rootCategories = categories.filter((c) => c.parent_id === null || c.category_type === "대분류");

    const handleMouseEnter = (id: number) => setHoveredMenu(id);
    const handleMouseLeave = () => setHoveredMenu(null);

    const handleInputChange = (value: string) => {
        setInputValue(value);
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
        debounceTimer.current = setTimeout(() => {
            onSearch(value.trim());
        }, 350);
    };

    const handleClear = () => {
        setInputValue("");
        onSearch("");
        desktopInputRef.current?.focus();
    };

    const handleMobileClear = () => {
        setInputValue("");
        onSearch("");
        mobileInputRef.current?.focus();
    };

    const openMobileSearch = () => {
        setIsMobileSearchOpen(true);
        setTimeout(() => mobileInputRef.current?.focus(), 50);
    };

    const closeMobileSearch = () => {
        setIsMobileSearchOpen(false);
        setInputValue("");
        onSearch("");
    };

    // Keyboard shortcut: "/" to focus search
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
                e.preventDefault();
                desktopInputRef.current?.focus();
            }
            if (e.key === "Escape" && isMobileSearchOpen) {
                closeMobileSearch();
            }
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isMobileSearchOpen]);

    return (
        <header className="sticky top-0 z-50 w-full bg-[#141414]/95 backdrop-blur-md border-b border-gray-800 transition-all duration-300">
            <div className="max-w-[1600px] mx-auto px-4 md:px-8 h-16 flex items-center justify-between">

                {/* Mobile Search Overlay */}
                {isMobileSearchOpen && (
                    <div className="absolute inset-0 flex items-center px-4 bg-[#141414] sm:hidden z-10">
                        <div className="flex items-center flex-1 gap-3">
                            <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <input
                                ref={mobileInputRef}
                                type="text"
                                value={inputValue}
                                placeholder="레시피 검색..."
                                autoFocus
                                className="flex-1 bg-transparent text-white text-base placeholder-gray-500 border-none outline-none"
                                onChange={(e) => handleInputChange(e.target.value)}
                                onKeyDown={(e) => e.key === "Escape" && closeMobileSearch()}
                            />
                            {inputValue && (
                                <button onClick={handleMobileClear} className="text-gray-400 hover:text-white p-1">
                                    <X size={18} />
                                </button>
                            )}
                            <button
                                onClick={closeMobileSearch}
                                className="text-gray-400 hover:text-white text-sm pl-2 border-l border-gray-700"
                            >
                                취소
                            </button>
                        </div>
                    </div>
                )}

                {/* Logo & Mobile Menu */}
                <div className="flex items-center gap-4">
                    <button className="md:hidden text-white hover:text-red-500" onClick={onMenuClick}>
                        <Menu size={24} />
                    </button>
                    <div className="flex items-baseline gap-3">
                        <Link
                            href="/"
                            onClick={() => {
                                setInputValue("");
                                onSearch("");
                            }}
                            className="text-xl md:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500 tracking-tight"
                        >
                            K-Food <span className="hidden sm:inline">백과사전</span>
                        </Link>
                        <span className="hidden lg:inline-flex items-center gap-1.5 text-xs text-gray-400 font-medium tracking-wide">
                            <span className="text-gray-500">|</span> &ldquo;오늘 뭐 해먹지?&rdquo; 고민 끝! 맛있는 레시피만 모았어요 🍳✨
                        </span>
                    </div>
                </div>

                {/* Global Navigation Bar (Desktop) */}
                <nav className="hidden md:flex h-full items-center gap-8 relative" onMouseLeave={handleMouseLeave}>
                    <Link
                        href="/"
                        onClick={() => {
                            setInputValue("");
                            onSearch("");
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        className="flex items-center gap-1.5 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                    >
                        <span className="text-red-500">🍲</span> 주메뉴
                    </Link>

                    <Link
                        href="/shorts"
                        className="flex items-center gap-1.5 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                    >
                        <span className="text-red-500">📱</span> 쇼츠 레시피
                    </Link>

                    <Link href="/trending" className="flex items-center gap-1.5 text-sm font-medium text-gray-300 hover:text-white transition-colors mr-6">
                        <span className="text-red-500">🔥</span> 인기 레시피
                    </Link>

                    {rootCategories.map((rootCat) => (
                        <div
                            key={rootCat.category_id}
                            className="h-full flex items-center cursor-pointer relative group"
                            onMouseEnter={() => handleMouseEnter(rootCat.category_id)}
                        >
                            <span className={`text-sm font-medium transition-colors ${hoveredMenu === rootCat.category_id ? "text-white" : "text-gray-300 hover:text-gray-100"}`}>
                                {rootCat.name}
                            </span>

                            {/* Active Indicator */}
                            <div className={`absolute bottom-0 left-0 w-full h-[2px] bg-red-600 transition-transform origin-left ${hoveredMenu === rootCat.category_id ? "scale-x-100" : "scale-x-0"}`} />
                        </div>
                    ))}

                    {/* Mega Menu Dropdown Panel */}
                    {hoveredMenu && (
                        <div className="absolute top-[100%] left-1/2 -translate-x-1/2 min-w-[400px] bg-[#1a1a1a] shadow-2xl border border-gray-800 rounded-b-xl overflow-hidden animate-in slide-in-from-top-2 duration-200">
                            <div className="p-6 grid grid-cols-3 gap-2">
                                {categories
                                    .filter(c => c.parent_id === hoveredMenu)
                                    .map(subCat => (
                                        <Link
                                            key={subCat.category_id}
                                            href={`/?category=${subCat.category_id}`}
                                            onClick={() => setHoveredMenu(null)}
                                            className="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                                        >
                                            {subCat.name}
                                        </Link>
                                    ))
                                }
                            </div>
                        </div>
                    )}
                </nav>

                {/* Search & Profile */}
                <div className="flex items-center gap-4">
                    {/* Search bar removed per user request */}
                    
                    {/* Stylized Hanja Stamp */}
                    <div className="hidden md:flex items-center gap-1.5 mr-5 cursor-default select-none group" title="식도락: 맛있는 음식을 먹는 즐거움">
                        {["食", "道", "樂"].map((char, i) => {
                            const transforms = [
                                '-rotate-12 translate-y-[2px] group-hover:-translate-y-[4px] group-hover:rotate-[-3deg]',
                                'rotate-12 -translate-y-[1px] group-hover:-translate-y-[8px] group-hover:rotate-[4deg]',
                                '-rotate-6 translate-y-[2px] group-hover:-translate-y-[3px] group-hover:rotate-[-1deg]'
                            ];
                            return (
                                <div 
                                    key={i} 
                                    className={`w-6 h-6 sm:w-7 sm:h-7 flex items-center justify-center rounded bg-gradient-to-br from-[#E63946] to-[#9B1D20] text-[#F1FAEE] font-serif text-sm sm:text-base font-black shadow-[1.5px_1.5px_0px_rgba(244,162,97,0.8)] border-[1px] border-[#D90429] transform transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${transforms[i]} group-hover:shadow-[2px_4px_0px_rgba(244,162,97,0.6)] relative overflow-hidden`}
                                >
                                    {/* Traditional seal texture effect */}
                                    <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] pointer-events-none mix-blend-overlay"></div>
                                    <span className="relative z-10 drop-shadow-sm">{char}</span>
                                </div>
                            );
                        })}
                    </div>

                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-red-600 to-orange-500 flex items-center justify-center text-sm font-bold cursor-pointer hover:ring-2 ring-offset-2 ring-offset-[#141414] ring-red-500 transition-all">
                        G
                    </div>
                </div>
            </div>
        </header>
    );
}
