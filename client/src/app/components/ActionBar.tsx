"use client";

/*
 * ActionBar — Floating bottom bar that appears when rows are selected (Design.txt §5)
 *
 * PATTERN: "Contextual Action Bar" (CAB)
 *   - Hidden when no rows are selected
 *   - Slides up from bottom when ≥1 row is selected
 *   - Shows selection count + bulk action buttons
 *
 * WHY A FLOATING BAR (not a toolbar in the header)?
 *   - Contextual: only shows when relevant (rows selected)
 *   - Doesn't clutter the header permanently
 *   - Common pattern in Gmail, Google Sheets, Notion
 *
 * ALTERNATIVE: Right-click context menu — works but less discoverable.
 *   The floating bar is immediately visible and touch-friendly.
 *
 * ANIMATION: CSS transform translateY — GPU-accelerated, doesn't
 *   trigger layout recalculations. Smooth even on low-end devices.
 */

interface ActionBarProps {
    selectedCount: number;
    onBulkEmail?: () => void;
    onBulkWhatsApp?: () => void;
    onBulkDelete?: () => void;
    onClearSelection?: () => void;
}

export default function ActionBar({
    selectedCount,
    onBulkEmail,
    onBulkWhatsApp,
    onBulkDelete,
    onClearSelection,
}: ActionBarProps) {
    const visible = selectedCount > 0;

    return (
        <div
            style={{
                position: "fixed",
                bottom: 24,
                left: "50%",
                transform: visible
                    ? "translateX(-50%) translateY(0)"
                    : "translateX(-50%) translateY(100px)",
                opacity: visible ? 1 : 0,
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                pointerEvents: visible ? "auto" : "none",
                zIndex: 70,

                /* Glassmorphism pill */
                background: "rgba(17, 17, 17, 0.9)",
                backdropFilter: "blur(16px)",
                WebkitBackdropFilter: "blur(16px)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                borderRadius: 16,
                padding: "10px 20px",
                display: "flex",
                alignItems: "center",
                gap: 12,
                boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
            }}
        >
            {/* Selection count */}
            <span
                style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    whiteSpace: "nowrap",
                }}
            >
                <span style={{ color: "var(--accent)", fontWeight: 700 }}>{selectedCount}</span> row
                {selectedCount !== 1 ? "s" : ""} selected
            </span>

            {/* Divider */}
            <div style={{ width: 1, height: 24, background: "var(--border-subtle)" }} />

            {/* Bulk Actions */}
            <ActionButton onClick={onBulkEmail} color="#4A90D9" icon="📧" label="Email All" />
            <ActionButton onClick={onBulkWhatsApp} color="#25D366" icon="💬" label="WhatsApp" />

            {/* Divider */}
            <div style={{ width: 1, height: 24, background: "var(--border-subtle)" }} />

            <ActionButton onClick={onBulkDelete} color="var(--danger)" icon="🗑️" label="Delete" />

            {/* Clear selection */}
            <button
                onClick={onClearSelection}
                style={{
                    background: "transparent",
                    border: "none",
                    color: "var(--text-tertiary)",
                    cursor: "pointer",
                    fontSize: 16,
                    padding: "4px 8px",
                    borderRadius: 6,
                    fontFamily: "inherit",
                }}
                title="Clear selection"
            >
                ✕
            </button>
        </div>
    );
}

/* ── Internal Action Button ───────────────────────────── */

function ActionButton({
    onClick,
    color,
    icon,
    label,
}: {
    onClick?: () => void;
    color: string;
    icon: string;
    label: string;
}) {
    return (
        <button
            onClick={onClick}
            style={{
                background: "transparent",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                color: color,
                cursor: "pointer",
                padding: "6px 12px",
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.15s ease",
                fontFamily: "inherit",
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
                e.currentTarget.style.borderColor = color;
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.08)";
            }}
        >
            <span>{icon}</span>
            <span>{label}</span>
        </button>
    );
}
