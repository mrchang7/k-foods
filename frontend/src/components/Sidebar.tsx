import { useState, useMemo } from "react";
import { X } from "lucide-react";

export interface Category {
    category_id: number;
    name: string;
    category_type: string;
    parent_id: number | null;
}

interface SidebarProps {
    categories: Category[];
    selectedCategories: number[];
    onChange: (categoryId: number) => void;
}

// 각 대분류에 이모지와 설명 추가
const GROUP_META: Record<string, { emoji: string; desc: string }> = {
    "음식 종류": { emoji: "🍜", desc: "어떤 요리를 찾나요?" },
    "주재료": { emoji: "🥩", desc: "재료로 골라보세요" },
    "조리 방법": { emoji: "🔥", desc: "어떻게 만드나요?" },
    "상황 & 목적": { emoji: "🎯", desc: "상황에 맞게 골라보세요" },
};

export default function Sidebar({ categories, selectedCategories, onChange }: SidebarProps) {
    const [openSections, setOpenSections] = useState<Record<number, boolean>>({});

    const toggleSection = (id: number) => {
        setOpenSections(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const facetGroups = useMemo(() => {
        return categories.filter(c => c.parent_id === null || c.category_type === "대분류");
    }, [categories]);

    const selectedCount = selectedCategories.length;

    return (
        <aside className="w-72 flex-shrink-0 bg-[#141414] border-r border-gray-800 hidden md:flex flex-col">
            {/* Header */}
            <div className="px-5 pt-6 pb-4 border-b border-gray-800">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-bold text-white">취향으로 찾기</h2>
                        <p className="text-xs text-gray-500 mt-0.5">원하는 조건을 선택해보세요</p>
                    </div>
                    {selectedCount > 0 && (
                        <button
                            onClick={() => selectedCategories.forEach(id => onChange(id))}
                            className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors bg-red-950/30 px-2 py-1 rounded-full border border-red-900/50"
                        >
                            <X size={11} />
                            전체 해제
                        </button>
                    )}
                </div>

                {/* Selected chips summary */}
                {selectedCount > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                        {selectedCategories.map(id => {
                            const cat = categories.find(c => c.category_id === id);
                            if (!cat) return null;
                            return (
                                <span
                                    key={id}
                                    onClick={() => onChange(id)}
                                    className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-600/20 border border-red-500/40 text-red-300 text-xs rounded-full cursor-pointer hover:bg-red-600/30 transition-colors"
                                >
                                    {cat.name}
                                    <X size={10} />
                                </span>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Category Groups */}
            <div className="flex-1 overflow-y-auto py-3 space-y-1 px-3">
                {facetGroups.map((group) => {
                    const options = categories.filter(c => c.parent_id === group.category_id);
                    if (options.length === 0) return null;

                    // Make all facet groups expanded by default
                    const isDefaultOpen = true;
                    const isOpen = openSections[group.category_id] ?? isDefaultOpen;
                    const meta = GROUP_META[group.name] ?? { emoji: "📂", desc: "" };
                    const selectedInGroup = options.filter(o => selectedCategories.includes(o.category_id));

                    return (
                        <div key={group.category_id} className="rounded-xl overflow-hidden">
                            {/* Group Header */}
                            <button
                                onClick={() => toggleSection(group.category_id)}
                                className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-white/5 transition-colors rounded-xl group"
                            >
                                <div className="flex items-center gap-2.5">
                                    <span className="text-lg leading-none">{meta.emoji}</span>
                                    <div className="text-left">
                                        <div className="flex items-center gap-2">
                                            <span className="text-sm font-semibold text-gray-100">{group.name}</span>
                                            {selectedInGroup.length > 0 && (
                                                <span className="bg-red-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center leading-tight">
                                                    {selectedInGroup.length}
                                                </span>
                                            )}
                                        </div>
                                        <span className="text-[11px] text-gray-500">{meta.desc}</span>
                                    </div>
                                </div>
                                <span className={`text-gray-500 transition-transform duration-200 text-xs ${isOpen ? "rotate-180" : ""}`}>▼</span>
                            </button>

                            {/* Options — Chip grid (항상 전체 보임) */}
                            {isOpen && (
                                <div className="px-3 pb-3 pt-1">
                                    <div className="flex flex-wrap gap-1.5">
                                        {options.map(option => {
                                            const isSelected = selectedCategories.includes(option.category_id);
                                            return (
                                                <button
                                                    key={option.category_id}
                                                    onClick={() => onChange(option.category_id)}
                                                    className={`
                                                        inline-flex items-center px-3 py-1.5 rounded-full text-[13px] font-medium
                                                        border transition-all duration-150 whitespace-nowrap
                                                        ${isSelected
                                                            ? "bg-red-600 border-red-600 text-white shadow-md shadow-red-900/30 scale-[1.03]"
                                                            : "bg-[#1e1e1e] border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white hover:bg-[#252525]"
                                                        }
                                                    `}
                                                >
                                                    {isSelected && <span className="mr-1 text-[11px]">✓</span>}
                                                    {option.name}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Divider */}
                            <div className="mx-3 h-px bg-gray-800/60" />
                        </div>
                    );
                })}
            </div>

            {/* Footer hint */}
            <div className="px-5 py-3 border-t border-gray-800">
                <p className="text-[11px] text-gray-600 text-center leading-relaxed">
                    각 그룹별로 <span className="text-gray-500">하나씩만</span> 선택할 수 있습니다<br />
                    그룹 간의 선택은 <span className="text-gray-500">AND</span> 조건으로 필터됩니다
                </p>
            </div>
        </aside>
    );
}
