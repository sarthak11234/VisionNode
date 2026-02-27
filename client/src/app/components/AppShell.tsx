"use client";

/*
 * AppShell — Layout wrapper that combines Sidebar + Header + Content area.
 *
 * LAYOUT STRATEGY: CSS Grid with fixed sidebar offset
 *   - Sidebar is position:fixed (floats above everything)
 *   - Content area has a left margin (64px) to avoid overlapping the sidebar
 *   - Header sits inside the content area, above the main panel
 *
 *   +--------+---------------------------+
 *   |        | Header                    |
 *   | Side   |---------------------------|
 *   | bar    | Content (children)        |
 *   |        |                           |
 *   +--------+---------------------------+
 *
 * WHY NOT CSS GRID for the full layout?
 *   The sidebar is fixed-position (doesn't scroll with content). CSS Grid
 *   items participate in normal flow. Mixing fixed + grid is awkward.
 *   A simple margin-left offset is the cleanest approach.
 *
 * ALTERNATIVE: Flexbox with overflow:hidden on sidebar — also works but
 *   fixed positioning gives us guaranteed viewport-height sidebar.
 */

import { useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface AppShellProps {
    children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
    const [activePage, setActivePage] = useState("sheets");

    return (
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            {/* Fixed sidebar */}
            <Sidebar activeItem={activePage} onNavigate={setActivePage} />

            {/* Main content area — offset by sidebar width */}
            <div
                style={{
                    marginLeft: 64, /* collapsed sidebar width */
                    display: "flex",
                    flexDirection: "column",
                    minHeight: "100vh",
                }}
            >
                <Header />

                {/* Content */}
                <main
                    style={{
                        flex: 1,
                        padding: 24,
                        overflow: "auto",
                    }}
                >
                    {children}
                </main>
            </div>
        </div>
    );
}
