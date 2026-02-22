"use client";

/*
 * DataGrid — Spreadsheet UI built on TanStack Table (Design.txt §2, §4)
 *
 * WHY TANSTACK TABLE (not AG Grid, Handsontable, or custom)?
 *   - Headless: We control 100% of the rendering → full design control
 *     for the HexaCore dark theme. AG Grid/Handsontable have their own
 *     DOM that's hard to override.
 *   - ~14KB gzipped vs AG Grid (~250KB) or Handsontable (~400KB)
 *   - React-first: hooks-based API, no imperative DOM manipulation
 *   - Free & MIT licensed (AG Grid community is limited, enterprise is $$$)
 *
 * TRADE-OFFS:
 *   - No built-in cell editing — we implement it ourselves (below)
 *   - No built-in virtualization — we'll add @tanstack/react-virtual
 *     in Phase 2 polish when row count > 1000
 *   - No drag-to-select ranges — can be added with a pointer event layer
 *
 * DATA FLOW:
 *   1. Parent passes `columns` (from sheet.column_schema) and `rows` (from API)
 *   2. DataGrid renders them via TanStack Table
 *   3. On cell edit → calls onCellEdit(rowId, columnKey, newValue)
 *   4. Parent PATCHes the API + WebSocket broadcasts the change
 *
 * EDITABLE CELLS ALGORITHM:
 *   - Click a cell → it becomes an <input> (controlled by local state)
 *   - Press Enter or blur → commit the edit via onCellEdit callback
 *   - Press Escape → cancel the edit
 *   This is a "click-to-edit" pattern, the simplest and most reliable.
 *   ALTERNATIVE: "always-editable" (every cell is always an input) —
 *   looks more like Excel but terrible for performance with 1000+ cells.
 */

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    type ColumnDef,
    type CellContext,
} from "@tanstack/react-table";

/* ── Types ────────────────────────────────────────────── */

export interface ColumnSchema {
    key: string;
    label: string;
    type?: "text" | "number" | "select";
}

export interface RowData {
    id: string;
    data: Record<string, string>;
}

interface DataGridProps {
    columns: ColumnSchema[];
    rows: RowData[];
    onCellEdit?: (rowId: string, columnKey: string, value: string) => void;
    onRowSelect?: (rowIds: string[]) => void;
}

/* ── Editable Cell ────────────────────────────────────── */

function EditableCell({
    value,
    rowId,
    columnKey,
    onCommit,
}: {
    value: string;
    rowId: string;
    columnKey: string;
    onCommit?: (rowId: string, columnKey: string, value: string) => void;
}) {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(value);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (editing) inputRef.current?.focus();
    }, [editing]);

    // Sync external value changes (e.g. from WebSocket)
    useEffect(() => {
        if (!editing) setDraft(value);
    }, [value, editing]);

    const commit = useCallback(() => {
        setEditing(false);
        if (draft !== value) {
            onCommit?.(rowId, columnKey, draft);
        }
    }, [draft, value, rowId, columnKey, onCommit]);

    if (editing) {
        return (
            <input
                ref={inputRef}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onBlur={commit}
                onKeyDown={(e) => {
                    if (e.key === "Enter") commit();
                    if (e.key === "Escape") {
                        setDraft(value);
                        setEditing(false);
                    }
                }}
                style={{
                    width: "100%",
                    background: "var(--bg-primary)",
                    border: "1px solid var(--accent)",
                    boxShadow: "var(--glow-accent)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-mono)",
                    fontSize: 13,
                    padding: "4px 8px",
                    outline: "none",
                    borderRadius: 2,
                }}
            />
        );
    }

    return (
        <div
            onDoubleClick={() => setEditing(true)}
            style={{
                padding: "4px 8px",
                cursor: "text",
                minHeight: 24,
                fontFamily: "var(--font-mono)",
                fontSize: 13,
            }}
            title="Double-click to edit"
        >
            {value || "\u00A0" /* non-breaking space for empty cells */}
        </div>
    );
}

/* ── Checkbox Column ──────────────────────────────────── */

const checkboxColumn: ColumnDef<RowData> = {
    id: "select",
    header: ({ table }) => (
        <input
            type="checkbox"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
            style={{ accentColor: "var(--accent)" }}
        />
    ),
    cell: ({ row }) => (
        <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            style={{ accentColor: "var(--accent)" }}
        />
    ),
    size: 40,
};

/* ── DataGrid Component ───────────────────────────────── */

export default function DataGrid({
    columns,
    rows,
    onCellEdit,
    onRowSelect,
}: DataGridProps) {
    const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});

    // Build TanStack column defs from our column schema
    // useMemo prevents re-creation on every render (react-hooks/exhaustive-deps)
    const tableColumns: ColumnDef<RowData>[] = useMemo(
        () => [
            checkboxColumn,
            ...columns.map((col) => ({
                id: col.key,
                accessorFn: (row: RowData) => row.data[col.key] ?? "",
                header: () => (
                    <span style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: 12, textTransform: "uppercase" as const, letterSpacing: "0.05em" }}>
                        {col.label}
                    </span>
                ),
                cell: (info: CellContext<RowData, unknown>) => (
                    <EditableCell
                        value={String(info.getValue())}
                        rowId={info.row.original.id}
                        columnKey={col.key}
                        onCommit={onCellEdit}
                    />
                ),
            })),
        ],
        [columns, onCellEdit]
    );

    const table = useReactTable({
        data: rows,
        columns: tableColumns,
        state: { rowSelection },
        onRowSelectionChange: (updater) => {
            const next = typeof updater === "function" ? updater(rowSelection) : updater;
            setRowSelection(next);
            // Notify parent of selected row IDs
            const selectedIds = Object.keys(next).filter((k) => next[k]).map((idx) => rows[Number(idx)]?.id).filter(Boolean);
            onRowSelect?.(selectedIds);
        },
        getCoreRowModel: getCoreRowModel(),
        getRowId: (row) => row.id,
    });

    return (
        <div style={{ overflowX: "auto", borderRadius: 8, border: "1px solid var(--border-subtle)" }}>
            <table
                style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    fontFamily: "var(--font-mono)",
                    fontSize: 13,
                }}
            >
                {/* ── Head ───────────────────────────────────── */}
                <thead>
                    {table.getHeaderGroups().map((hg) => (
                        <tr key={hg.id}>
                            {hg.headers.map((header) => (
                                <th
                                    key={header.id}
                                    style={{
                                        padding: "10px 12px",
                                        textAlign: "left",
                                        borderBottom: "1px solid var(--border)",
                                        background: "var(--bg-secondary)",
                                        color: "var(--text-secondary)",
                                        position: "sticky",
                                        top: 0,
                                        zIndex: 10,
                                        width: header.getSize(),
                                    }}
                                >
                                    {header.isPlaceholder
                                        ? null
                                        : flexRender(header.column.columnDef.header, header.getContext())}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>

                {/* ── Body ───────────────────────────────────── */}
                <tbody>
                    {table.getRowModel().rows.length === 0 ? (
                        <tr>
                            <td
                                colSpan={tableColumns.length}
                                style={{
                                    textAlign: "center",
                                    padding: 40,
                                    color: "var(--text-tertiary)",
                                }}
                            >
                                No rows yet — import a CSV or create a row
                            </td>
                        </tr>
                    ) : (
                        table.getRowModel().rows.map((row) => (
                            <tr
                                key={row.id}
                                style={{
                                    borderBottom: "1px solid var(--border-subtle)",
                                    background: row.getIsSelected()
                                        ? "rgba(9, 5, 254, 0.08)"
                                        : "transparent",
                                    transition: "background 0.1s ease",
                                }}
                                onMouseEnter={(e) => {
                                    if (!row.getIsSelected())
                                        e.currentTarget.style.background = "var(--bg-tertiary)";
                                }}
                                onMouseLeave={(e) => {
                                    if (!row.getIsSelected())
                                        e.currentTarget.style.background = "transparent";
                                }}
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <td
                                        key={cell.id}
                                        style={{
                                            padding: "2px 4px",
                                            borderRight: "1px solid var(--border-subtle)",
                                        }}
                                    >
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
}
