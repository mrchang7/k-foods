import { useState, useMemo } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

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

export default function Sidebar({ categories, selectedCategories, onChange }: SidebarProps) {
    // State to manage which accordions are open
    const [openSections, setOpenSections] = useState<Record<number, boolean>>({});

    const toggleSection = (id: number) => {
        setOpenSections(prev => ({ ...prev, [id]: !prev[id] }));
    };

    // Find top-level categories to act as Facet Groups (e.g. 주재료, 조리법)
    const facetGroups = useMemo(() => {
        return categories.filter(c => c.parent_id === null || c.category_type === '대분류');
    }, [categories]);

    return (
        <aside className="w-72 flex-shrink-0 bg-[#141414] border-r border-gray-800 h-[calc(100vh-64px)] overflow-y-auto hidden md:block custom-scrollbar">
            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-bold text-white tracking-tight">취향 검색</h2>
                    {selectedCategories.length > 0 && (
                        <span className="text-xs text-red-500 font-medium">{selectedCategories.length}개 선택됨</span>
                    )}
                </div>

                <div className="space-y-4">
                    {facetGroups.map((group) => {
                        // Find all descendants of this group to show as checkboxes
                        // Simple 1-level children for faceted search demo
                        const options = categories.filter(c => c.parent_id === group.category_id);

                        // If group has no children, don't show it as a facet section
                        if (options.length === 0) return null;

                        const isOpen = openSections[group.category_id] ?? true; // Default open
                        const selectedCountInGroup = options.filter(o => selectedCategories.includes(o.category_id)).length;

                        return (
                            <div key={group.category_id} className="border border-gray-800 rounded-lg overflow-hidden bg-[#1a1a1a]">
                                <button
                                    onClick={() => toggleSection(group.category_id)}
                                    className="w-full flex items-center justify-between p-4 hover:bg-[#202020] transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-sm font-semibold text-gray-200">{group.name}</h3>
                                        {selectedCountInGroup > 0 && (
                                            <span className="bg-red-600/20 text-red-500 text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                                                {selectedCountInGroup}
                                            </span>
                                        )}
                                    </div>
                                    {isOpen ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-500" />}
                                </button>

                                {isOpen && (
                                    <div className="p-4 pt-0 space-y-3">
                                        {options.map(option => {
                                            const isSelected = selectedCategories.includes(option.category_id);
                                            // Mock video count for faceted UI demo purposes
                                            const mockCount = Math.floor(Math.random() * 100) + 10;

                                            return (
                                                <label key={option.category_id} className="flex items-center justify-between cursor-pointer group">
                                                    <div className="flex items-center gap-3">
                                                        <div className="relative flex items-center justify-center">
                                                            <input
                                                                type="checkbox"
                                                                checked={isSelected}
                                                                onChange={() => onChange(option.category_id)}
                                                                className="appearance-none w-4 h-4 border border-gray-600 rounded-sm bg-transparent checked:bg-red-600 checked:border-red-600 transition-colors group-hover:border-gray-400"
                                                            />
                                                            {isSelected && (
                                                                <svg className="absolute w-3 h-3 text-white pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                                </svg>
                                                            )}
                                                        </div>
                                                        <span className={`text-sm transition-colors ${isSelected ? 'text-white font-medium' : 'text-gray-400 group-hover:text-gray-300'}`}>
                                                            {option.name}
                                                        </span>
                                                    </div>
                                                    <span className="text-xs text-gray-600 group-hover:text-gray-500">
                                                        ({mockCount})
                                                    </span>
                                                </label>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </aside>
    );
}
