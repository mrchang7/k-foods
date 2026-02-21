"use client";

import { useState } from "react";
import Link from "next/link";
import { Category } from "./Sidebar";
import { Search, Menu, X } from "lucide-react";

interface HeaderProps {
    categories: Category[];
    onMenuClick: () => void;
}

export default function Header({ categories, onMenuClick }: HeaderProps) {
    const [hoveredMenu, setHoveredMenu] = useState<number | null>(null);

    // Group root categories (대분류)
    const rootCategories = categories.filter((c) => c.parent_id === null || c.category_type === "대분류");

    const handleMouseEnter = (id: number) => setHoveredMenu(id);
    const handleMouseLeave = () => setHoveredMenu(null);

    return (
        <header className="sticky top-0 z-50 w-full bg-[#141414]/95 backdrop-blur-md border-b border-gray-800 transition-all duration-300">
            <div className="max-w-[1600px] mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
                {/* Logo & Mobile Menu */}
                <div className="flex items-center gap-4">
                    <button className="md:hidden text-white hover:text-red-500" onClick={onMenuClick}>
                        <Menu size={24} />
                    </button>
                    <Link href="/" className="text-xl md:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500 tracking-tight">
                        K-Food <span className="hidden sm:inline">백과사전</span>
                    </Link>
                </div>

                {/* Global Navigation Bar (Desktop) */}
                <nav className="hidden md:flex h-full items-center gap-8 relative" onMouseLeave={handleMouseLeave}>
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
                <div className="flex items-center gap-6">
                    <div className="relative group hidden sm:block">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-white" />
                        <input
                            type="text"
                            placeholder="레시피 검색..."
                            className="bg-[#202020] border border-gray-700 text-white text-sm rounded-full pl-10 pr-4 py-1.5 focus:outline-none focus:border-red-500 focus:bg-[#141414] transition-all w-48 focus:w-64"
                        />
                    </div>
                    <button className="sm:hidden text-white">
                        <Search size={20} />
                    </button>

                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-red-600 to-orange-500 flex items-center justify-center text-sm font-bold cursor-pointer hover:ring-2 ring-offset-2 ring-offset-[#141414] ring-red-500 transition-all">
                        G
                    </div>
                </div>
            </div>
        </header>
    );
}
