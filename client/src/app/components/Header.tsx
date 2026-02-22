"use client";

/*
 * Header — Top bar with command-center stats (Design.txt §2)
 *
 * Displays live system metrics:
 *   - "Active Agents: N"  — how many rules are currently enabled
 *   - "System Latency: Xms" — placeholder until we add real ping
 *
 * WHY A FIXED HEADER (not sticky)?
 *   Fixed keeps the header visible even when sheet content scrolls.
 *   The header is only ~48px, so it doesn't eat too much vertical space.
 *
 * ALTERNATIVE: Merge into sidebar top area — saves vertical space but
 *   crowds the sidebar. Separate header is standard for data-heavy UIs.
 */

interface HeaderProps {
    activeAgents?: number;
    latencyMs?: number;
    sheetName?: string;
}

export default function Header({
    activeAgents = 0,
    latencyMs = 24,
    sheetName = "Untitled Sheet",
}: HeaderProps) {
    return (
        <header
            style={{
                height: 48,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0 24px",
                borderBottom: "1px solid var(--border-subtle)",
                background: "var(--bg-secondary)",
                fontFamily: "var(--font-mono)",
                fontSize: 12,
                color: "var(--text-secondary)",
                flexShrink: 0,
            }}
        >
            {/* Left — Sheet name */}
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <h1
                    style={{
                        fontFamily: "var(--font-heading)",
                        fontSize: 16,
                        fontWeight: 700,
                        color: "var(--text-primary)",
                        margin: 0,
                    }}
                >
                    {sheetName}
                </h1>
            </div>

            {/* Right — System stats */}
            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                {/* Active Agents badge */}
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span
                        style={{
                            width: 6,
                            height: 6,
                            borderRadius: "50%",
                            background: activeAgents > 0 ? "var(--success)" : "var(--text-tertiary)",
                            boxShadow: activeAgents > 0 ? "var(--glow-success)" : "none",
                            display: "inline-block",
                        }}
                    />
                    <span>Active Agents: {activeAgents}</span>
                </div>

                {/* Latency */}
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span
                        style={{
                            width: 6,
                            height: 6,
                            borderRadius: "50%",
                            background: latencyMs < 100 ? "var(--success)" : "var(--warning)",
                            display: "inline-block",
                        }}
                    />
                    <span>Latency: {latencyMs}ms</span>
                </div>
            </div>
        </header>
    );
}
