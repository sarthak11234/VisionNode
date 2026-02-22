"use client";

/*
 * Sidebar — Left-aligned vertical navigation (Design.txt §2)
 *
 * PATTERN: Icon-only, expand-on-hover
 *   - Collapsed: 64px wide, shows only icons
 *   - Expanded: 240px wide, shows icon + label on hover
 *   - Transition: CSS width + opacity animation (no JS state needed)
 *
 * WHY CSS-ONLY EXPAND (not React state)?
 *   - Zero re-renders — the browser's compositor handles the animation
 *   - GPU-accelerated since we only animate width + opacity
 *   - Simpler code — no useState, no onClick handlers
 *
 * ALTERNATIVE: Framer Motion `layout` animation — smoother spring physics
 *   but adds ~30KB JS. We'll upgrade to Framer Motion in Phase 2 polish
 *   if the CSS version feels too rigid.
 *
 * GLASSMORPHISM EFFECT:
 *   - Semi-transparent background (rgba white 5%)
 *   - backdrop-filter: blur(16px) — frosted glass effect
 *   - Subtle border on the right edge
 *   This makes the sidebar feel like it floats above the content.
 */

import { useState } from "react";

// SVG icon paths — lightweight, no icon library dependency
// ALTERNATIVE: lucide-react (~150KB) or heroicons. We inline SVGs to save
// bundle size. Can switch to lucide later if we need 100+ icons.
const icons = {
    sheets: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0 1 12 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 0v1.5c0 .621-.504 1.125-1.125 1.125" />
        </svg>
    ),
    agents: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
        </svg>
    ),
    settings: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 0 1 1.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.559.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.894.149c-.424.07-.764.383-.929.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 0 1-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.109l-.738.527a1.125 1.125 0 0 1-1.45-.12l-.773-.774a1.125 1.125 0 0 1-.12-1.45l.527-.737c.25-.35.272-.806.108-1.204-.165-.397-.506-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.108-1.204l-.526-.738a1.125 1.125 0 0 1 .12-1.45l.773-.773a1.125 1.125 0 0 1 1.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894Z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
        </svg>
    ),
    home: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955a1.126 1.126 0 0 1 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
    ),
};

interface NavItem {
    id: string;
    label: string;
    icon: React.ReactNode;
}

const navItems: NavItem[] = [
    { id: "home", label: "Dashboard", icon: icons.home },
    { id: "sheets", label: "Sheets", icon: icons.sheets },
    { id: "agents", label: "Agents", icon: icons.agents },
    { id: "settings", label: "Settings", icon: icons.settings },
];

interface SidebarProps {
    activeItem?: string;
    onNavigate?: (id: string) => void;
}

export default function Sidebar({ activeItem = "sheets", onNavigate }: SidebarProps) {
    const [hovered, setHovered] = useState(false);

    return (
        <aside
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            className="sidebar"
            style={{
                /* Glassmorphism */
                position: "fixed",
                left: 0,
                top: 0,
                height: "100vh",
                width: hovered ? 200 : 64,
                background: "var(--bg-surface)",
                backdropFilter: "blur(16px)",
                WebkitBackdropFilter: "blur(16px)",
                borderRight: "1px solid var(--border-subtle)",
                display: "flex",
                flexDirection: "column",
                padding: "16px 0",
                transition: "width 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
                zIndex: 50,
                overflow: "hidden",
            }}
        >
            {/* Logo */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: "0 20px",
                    marginBottom: 32,
                    whiteSpace: "nowrap",
                }}
            >
                <div
                    style={{
                        width: 24,
                        height: 24,
                        borderRadius: 6,
                        background: "var(--accent)",
                        boxShadow: "var(--glow-accent)",
                        flexShrink: 0,
                    }}
                />
                <span
                    style={{
                        fontFamily: "var(--font-heading)",
                        fontWeight: 700,
                        fontSize: 16,
                        color: "var(--text-primary)",
                        opacity: hovered ? 1 : 0,
                        transition: "opacity 0.2s ease",
                    }}
                >
                    SheetAgent
                </span>
            </div>

            {/* Nav Items */}
            <nav style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
                {navItems.map((item) => {
                    const isActive = item.id === activeItem;
                    return (
                        <button
                            key={item.id}
                            onClick={() => onNavigate?.(item.id)}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                                padding: "10px 20px",
                                border: "none",
                                background: isActive ? "rgba(9, 5, 254, 0.15)" : "transparent",
                                color: isActive ? "var(--accent)" : "var(--text-secondary)",
                                cursor: "pointer",
                                whiteSpace: "nowrap",
                                borderLeft: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                                transition: "all 0.15s ease",
                                fontSize: 14,
                                fontFamily: "inherit",
                            }}
                            onMouseEnter={(e) => {
                                if (!isActive) e.currentTarget.style.background = "rgba(255,255,255,0.03)";
                            }}
                            onMouseLeave={(e) => {
                                if (!isActive) e.currentTarget.style.background = "transparent";
                            }}
                        >
                            <span style={{ flexShrink: 0 }}>{item.icon}</span>
                            <span
                                style={{
                                    opacity: hovered ? 1 : 0,
                                    transition: "opacity 0.2s ease",
                                }}
                            >
                                {item.label}
                            </span>
                        </button>
                    );
                })}
            </nav>
        </aside>
    );
}
