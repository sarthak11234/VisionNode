"use client";

/*
 * AgentSidebar — Floating right-hand panel (Design.txt §3)
 *
 * Shows a list of automation rules as glassmorphic cards.
 * Each card displays: trigger condition → action type.
 *
 * PATTERN: Slide-in panel with toggle button
 *   - Collapsed: a small FAB (floating action button) at the right edge
 *   - Expanded: 320px panel slides in from the right
 *
 * WHY A FLOATING PANEL (not a fixed sidebar)?
 *   The spreadsheet needs maximum horizontal space. A fixed right sidebar
 *   permanently eats 320px. A floating panel overlays on demand.
 *
 * GLASSMORPHISM RECIPE:
 *   background: rgba(255, 255, 255, 0.05)
 *   backdrop-filter: blur(16px)
 *   border: 1px solid rgba(255, 255, 255, 0.08)
 *   This creates the frosted-glass look from Design.txt §4.
 */

import { useState, useRef, useEffect } from "react";

/* ── Types ────────────────────────────────────────────── */

export interface AgentRule {
    id: string;
    triggerColumn: string;
    triggerValue: string;
    actionType: "whatsapp" | "email" | "create_group";
    enabled: boolean;
}

interface AgentSidebarProps {
    rules: AgentRule[];
    onToggleRule?: (ruleId: string, enabled: boolean) => void;
    onAddRule?: (rule: Omit<AgentRule, "id" | "enabled">) => void;
    columns?: { key: string; label: string }[];
    logs?: { id: string; rule_id: string; row_id: string; status: string; message: string; timestamp: string }[];
}

/* ── Action Type Config ───────────────────────────────── */

const actionMeta: Record<string, { label: string; color: string; icon: string }> = {
    whatsapp: { label: "WhatsApp", color: "#25D366", icon: "💬" },
    email: { label: "Email", color: "#4A90D9", icon: "📧" },
    create_group: { label: "Create Group", color: "#FF6B6B", icon: "👥" },
};

/* ── Component ────────────────────────────────────────── */

export default function AgentSidebar({ rules, onToggleRule, onAddRule, columns = [], logs = [] }: AgentSidebarProps) {
    const [open, setOpen] = useState(false);
    const [isAdding, setIsAdding] = useState(false);
    const logContainerRef = useRef<HTMLDivElement>(null);

    // Auto-scroll logs to bottom
    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    // Form State
    const [triggerColumn, setTriggerColumn] = useState("");
    const [triggerValue, setTriggerValue] = useState("");
    const [actionType, setActionType] = useState<AgentRule["actionType"]>("email");

    const handleSaveRule = () => {
        if (!triggerColumn || !triggerValue) return;
        onAddRule?.({ triggerColumn, triggerValue, actionType });
        setIsAdding(false);
        setTriggerColumn("");
        setTriggerValue("");
    };

    return (
        <>
            {/* Toggle FAB */}
            <button
                onClick={() => setOpen(!open)}
                style={{
                    position: "fixed",
                    right: open ? 320 : 0,
                    top: "50%",
                    transform: "translateY(-50%)",
                    width: 40,
                    height: 80,
                    background: "var(--accent)",
                    border: "none",
                    borderRadius: "8px 0 0 8px",
                    color: "#fff",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 18,
                    boxShadow: "var(--glow-accent)",
                    transition: "right 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    zIndex: 60,
                }}
                title={open ? "Close agent panel" : "Open agent panel"}
            >
                {open ? "›" : "‹"}
            </button>

            {/* Panel */}
            <aside
                style={{
                    position: "fixed",
                    right: open ? 0 : -320,
                    top: 0,
                    width: 320,
                    height: "100vh",
                    background: "rgba(17, 17, 17, 0.85)",
                    backdropFilter: "blur(16px)",
                    WebkitBackdropFilter: "blur(16px)",
                    borderLeft: "1px solid rgba(255, 255, 255, 0.08)",
                    transition: "right 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    zIndex: 55,
                    display: "flex",
                    flexDirection: "column",
                    overflow: "hidden",
                }}
            >
                {/* Header */}
                <div
                    style={{
                        padding: "20px 16px 12px",
                        borderBottom: "1px solid var(--border-subtle)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                    }}
                >
                    <h2
                        style={{
                            margin: 0,
                            fontFamily: "var(--font-heading)",
                            fontSize: 16,
                            fontWeight: 700,
                            color: "var(--text-primary)",
                        }}
                    >
                        🤖 Agent Rules
                    </h2>
                    <button
                        onClick={() => setIsAdding(!isAdding)}
                        style={{
                            background: isAdding ? "rgba(255, 255, 255, 0.1)" : "var(--accent)",
                            border: isAdding ? "1px solid rgba(255, 255, 255, 0.2)" : "none",
                            color: "#fff",
                            padding: "6px 12px",
                            borderRadius: 6,
                            fontSize: 12,
                            fontWeight: 600,
                            cursor: "pointer",
                            fontFamily: "inherit",
                        }}
                    >
                        {isAdding ? "Cancel" : "+ Add Rule"}
                    </button>
                </div>

                {/* Add Rule Form */}
                {isAdding && (
                    <div style={{
                        padding: 16,
                        background: "rgba(0,0,0,0.2)",
                        borderBottom: "1px solid var(--border-subtle)",
                        display: "flex",
                        flexDirection: "column",
                        gap: 12
                    }}>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                            <label style={{ fontSize: 11, color: "var(--text-tertiary)", textTransform: "uppercase" }}>When Column</label>
                            <select
                                value={triggerColumn}
                                onChange={e => setTriggerColumn(e.target.value)}
                                style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", color: "#fff", padding: 6, borderRadius: 4, outline: "none" }}
                            >
                                <option value="" disabled>Select Column...</option>
                                {columns.map(col => <option key={col.key} value={col.key}>{col.label}</option>)}
                            </select>
                        </div>

                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                            <label style={{ fontSize: 11, color: "var(--text-tertiary)", textTransform: "uppercase" }}>Equals To</label>
                            <input
                                placeholder="e.g. Shortlisted"
                                value={triggerValue}
                                onChange={e => setTriggerValue(e.target.value)}
                                style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", color: "#fff", padding: 6, borderRadius: 4, outline: "none" }}
                            />
                        </div>

                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                            <label style={{ fontSize: 11, color: "var(--text-tertiary)", textTransform: "uppercase" }}>Then Do</label>
                            <select
                                value={actionType}
                                onChange={e => setActionType(e.target.value as AgentRule["actionType"])}
                                style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", color: "#fff", padding: 6, borderRadius: 4, outline: "none" }}
                            >
                                <option value="email">📧 Send Email</option>
                                <option value="whatsapp">💬 Send WhatsApp</option>
                                <option value="create_group">👥 Create Group</option>
                            </select>
                        </div>

                        <button
                            onClick={handleSaveRule}
                            disabled={!triggerColumn || !triggerValue}
                            style={{
                                background: (!triggerColumn || !triggerValue) ? "rgba(255,255,255,0.1)" : "var(--success)",
                                color: (!triggerColumn || !triggerValue) ? "var(--text-tertiary)" : "#000",
                                border: "none",
                                padding: "8px",
                                borderRadius: 6,
                                fontWeight: 700,
                                cursor: (!triggerColumn || !triggerValue) ? "not-allowed" : "pointer",
                                marginTop: 4
                            }}
                        >
                            Save Rule
                        </button>
                    </div>
                )}

                {/* Rule Cards */}
                <div style={{ flex: 1, overflowY: "auto", padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
                    {rules.length === 0 ? (
                        <div
                            style={{
                                textAlign: "center",
                                padding: 40,
                                color: "var(--text-tertiary)",
                                fontSize: 13,
                            }}
                        >
                            No rules yet. Click &quot;+ Add Rule&quot; to create one.
                        </div>
                    ) : (
                        rules.map((rule) => {
                            const meta = actionMeta[rule.actionType] || actionMeta.email;
                            return (
                                <div
                                    key={rule.id}
                                    style={{
                                        background: "rgba(255, 255, 255, 0.04)",
                                        border: "1px solid rgba(255, 255, 255, 0.06)",
                                        borderRadius: 10,
                                        padding: 14,
                                        transition: "border-color 0.2s ease",
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.15)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)";
                                    }}
                                >
                                    {/* Condition */}
                                    <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8, fontFamily: "var(--font-mono)" }}>
                                        If <span style={{ color: "var(--accent)", fontWeight: 600 }}>{rule.triggerColumn}</span>
                                        {" = "}
                                        <span style={{ color: "var(--text-primary)" }}>&quot;{rule.triggerValue}&quot;</span>
                                    </div>

                                    {/* Action */}
                                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                            <span>{meta.icon}</span>
                                            <span
                                                style={{
                                                    fontSize: 13,
                                                    fontWeight: 600,
                                                    color: meta.color,
                                                }}
                                            >
                                                {meta.label}
                                            </span>
                                        </div>

                                        {/* Toggle switch */}
                                        <button
                                            onClick={() => onToggleRule?.(rule.id, !rule.enabled)}
                                            style={{
                                                width: 36,
                                                height: 20,
                                                borderRadius: 10,
                                                border: "none",
                                                background: rule.enabled ? "var(--success)" : "var(--text-tertiary)",
                                                cursor: "pointer",
                                                position: "relative",
                                                transition: "background 0.2s ease",
                                            }}
                                        >
                                            <span
                                                style={{
                                                    position: "absolute",
                                                    top: 2,
                                                    left: rule.enabled ? 18 : 2,
                                                    width: 16,
                                                    height: 16,
                                                    borderRadius: "50%",
                                                    background: "#fff",
                                                    transition: "left 0.2s ease",
                                                }}
                                            />
                                        </button>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {/* Process Log (Live Preview) */}
                <div
                    style={{
                        borderTop: "1px solid var(--border-subtle)",
                        padding: "10px 14px",
                        fontFamily: "var(--font-mono)",
                        fontSize: 11,
                        color: "var(--text-tertiary)",
                        background: "rgba(0, 0, 0, 0.3)",
                        height: 150,
                        display: "flex",
                        flexDirection: "column",
                    }}
                >
                    <div style={{ marginBottom: 4, fontWeight: 600, color: "var(--text-secondary)", flexShrink: 0 }}>
                        ▸ Process Log
                    </div>

                    <div
                        ref={logContainerRef}
                        style={{
                            flex: 1,
                            overflowY: "auto",
                            display: "flex",
                            flexDirection: "column",
                            gap: 4
                        }}
                    >
                        {logs.length === 0 ? (
                            <div>&gt; System ready. Listening for agent tasks...</div>
                        ) : (
                            logs.map(log => (
                                <div key={log.id} style={{
                                    color: log.status === "failed" ? "var(--danger)" :
                                        log.status === "success" ? "var(--success)" : "var(--accent)"
                                }}>
                                    <span style={{ opacity: 0.5 }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span>{" "}
                                    {log.message}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </aside>
        </>
    );
}
