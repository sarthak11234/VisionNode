"use client";

import AppShell from "./components/AppShell";
import DataGrid, { type ColumnSchema, type RowData } from "./components/DataGrid";
import AgentSidebar, { type AgentRule } from "./components/AgentSidebar";

/*
 * DEMO DATA — mimics a college-fest audition sheet.
 * This will be replaced with API calls in Phase 3.
 */

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

export default function Home() {
  return (
    <AppShell>
      <DataGrid
        columns={demoColumns}
        rows={demoRows}
        onCellEdit={(rowId, col, val) => {
          console.log(`Edit: row=${rowId} col=${col} val=${val}`);
        }}
        onRowSelect={(ids) => {
          console.log("Selected:", ids);
        }}
      />
      <AgentSidebar
        rules={demoRules}
        onToggleRule={(id, enabled) => console.log(`Toggle: ${id} → ${enabled}`)}
        onAddRule={() => console.log("Add rule clicked")}
      />
    </AppShell>
  );
}


