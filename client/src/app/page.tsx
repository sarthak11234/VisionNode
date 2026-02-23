"use client";

/*
 * Home Page — Wired to backend API via TanStack Query hooks
 *
 * DATA FLOW:
 *   1. useRows(sheetId)       → fetches rows from GET /sheets/{id}/rows
 *   2. useSheet(sheetId)      → fetches column schema from GET /sheets/{id}
 *   3. useAgentRules(sheetId) → fetches rules from GET /agent-rules?sheet_id=...
 *   4. useMutateRow(sheetId)  → optimistic PATCH on cell edit
 *   5. useSheetSocket(sheetId)→ WebSocket for real-time row updates
 *
 * FALLBACK: If no sheetId is set (first load, no backend running),
 *   we render the demo data so the UI is always visible during dev.
 */

import { useState, useCallback } from "react";
import AppShell from "./components/AppShell";
import DataGrid, { type ColumnSchema, type RowData } from "./components/DataGrid";
import AgentSidebar, { type AgentRule } from "./components/AgentSidebar";
import ActionBar from "./components/ActionBar";
import {
  useSheet,
  useRows,
  useMutateRow,
  useDeleteRow,
  useAgentRules,
  useToggleRule,
} from "@/hooks/useSheetData";
import { useSheetSocket } from "@/hooks/useSheetSocket";

/* ── Demo Data (fallback when backend is not connected) ── */

const demoColumns: ColumnSchema[] = [
  { key: "name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "phone", label: "Phone" },
  { key: "talent", label: "Talent" },
  { key: "score", label: "Score", type: "number" },
  { key: "status", label: "Status", type: "select" },
];

const demoRows: RowData[] = [
  { id: "1", data: { name: "Arjun Mehta", email: "arjun@fest.in", phone: "9876543210", talent: "Beatboxing", score: "92", status: "Shortlisted" } },
  { id: "2", data: { name: "Priya Sharma", email: "priya@fest.in", phone: "9123456780", talent: "Singing", score: "88", status: "Pending" } },
  { id: "3", data: { name: "Rohan Gupta", email: "rohan@fest.in", phone: "9988776655", talent: "Stand-up", score: "75", status: "Rejected" } },
  { id: "4", data: { name: "Sara Khan", email: "sara@fest.in", phone: "9001122334", talent: "Dance", score: "95", status: "Shortlisted" } },
  { id: "5", data: { name: "Dev Patel", email: "dev@fest.in", phone: "9556677889", talent: "Magic", score: "81", status: "Pending" } },
];

const demoRules: AgentRule[] = [
  { id: "r1", triggerColumn: "status", triggerValue: "Shortlisted", actionType: "email", enabled: true },
  { id: "r2", triggerColumn: "status", triggerValue: "Shortlisted", actionType: "whatsapp", enabled: true },
  { id: "r3", triggerColumn: "score", triggerValue: "90", actionType: "create_group", enabled: false },
];

/* ── Page Component ───────────────────────────────────── */

export default function Home() {
  // TODO: Replace with dynamic sheet selection (Phase 3 polish)
  const [sheetId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Data hooks — enabled only when sheetId is set
  const { data: sheet } = useSheet(sheetId);
  const { data: apiRows } = useRows(sheetId);
  const { data: apiRules } = useAgentRules(sheetId);
  const mutateRow = useMutateRow(sheetId ?? "");
  const deleteRow = useDeleteRow(sheetId ?? "");
  const toggleRule = useToggleRule();

  // WebSocket for live updates
  useSheetSocket(sheetId);

  // Resolve data: API if connected, demo as fallback
  const columns: ColumnSchema[] = (sheet?.column_schema as ColumnSchema[]) ?? demoColumns;
  const rows: RowData[] = apiRows ?? demoRows;
  const rules: AgentRule[] = apiRules?.map((r) => ({
    id: r.id,
    triggerColumn: r.trigger_column,
    triggerValue: r.trigger_value,
    actionType: r.action_type as AgentRule["actionType"],
    enabled: r.enabled,
  })) ?? demoRules;

  // Cell edit handler — optimistic PATCH or console log in demo mode
  const handleCellEdit = useCallback(
    (rowId: string, columnKey: string, value: string) => {
      if (sheetId) {
        mutateRow.mutate({ rowId, data: { [columnKey]: value } });
      } else {
        console.log(`[demo] Edit: row=${rowId} col=${columnKey} val=${value}`);
      }
    },
    [sheetId, mutateRow],
  );

  // Bulk delete handler
  const handleBulkDelete = useCallback(() => {
    if (sheetId) {
      selectedIds.forEach((id) => deleteRow.mutate(id));
    } else {
      console.log("[demo] Bulk delete:", selectedIds);
    }
    setSelectedIds([]);
  }, [sheetId, selectedIds, deleteRow]);

  return (
    <AppShell>
      <DataGrid
        columns={columns}
        rows={rows}
        onCellEdit={handleCellEdit}
        onRowSelect={setSelectedIds}
      />
      <AgentSidebar
        rules={rules}
        onToggleRule={(id, enabled) => {
          if (sheetId) {
            toggleRule.mutate({ ruleId: id, enabled });
          } else {
            console.log(`[demo] Toggle: ${id} → ${enabled}`);
          }
        }}
        onAddRule={() => console.log("Add rule clicked")}
      />
      <ActionBar
        selectedCount={selectedIds.length}
        onBulkEmail={() => console.log("Bulk email:", selectedIds)}
        onBulkWhatsApp={() => console.log("Bulk WhatsApp:", selectedIds)}
        onBulkDelete={handleBulkDelete}
        onClearSelection={() => setSelectedIds([])}
      />
    </AppShell>
  );
}
