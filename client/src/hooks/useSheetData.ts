/*
 * useSheet — Data hooks for sheet CRUD operations
 *
 * PATTERN: Each hook wraps a TanStack Query useQuery/useMutation.
 *   - useQuery for reads (cached, auto-refetch)
 *   - useMutation for writes (with optimistic updates for cell edits)
 *
 * WHY TANSTACK QUERY (not SWR, Redux Toolkit Query, or raw useEffect)?
 *   - Built-in cache invalidation + optimistic updates
 *   - Devtools for debugging cache state
 *   - Fine-grained control over stale/cache/retry behavior
 *   - ~13KB gzipped (same ballpark as SWR)
 *   SWR is simpler but lacks mutation support. RTK Query requires Redux.
 *
 * OPTIMISTIC UPDATES (for cell edits):
 *   When a user edits a cell, we immediately update the local cache
 *   before the API responds. If the API fails, we rollback to the
 *   previous state. This makes edits feel instant (0ms perceived latency).
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

/* ── Types (matching backend Pydantic schemas) ────────── */

interface WorkspaceResponse {
    id: string;
    name: string;
    owner_id: string | null;
    created_at: string;
}

interface SheetResponse {
    id: string;
    workspace_id: string;
    name: string;
    column_schema: Array<{ key: string; label: string; type?: string }>;
    created_at: string;
}

interface RowResponse {
    id: string;
    sheet_id: string;
    data: Record<string, string>;
    row_order: string;
    created_at: string;
    updated_at: string;
}

interface AgentRuleResponse {
    id: string;
    sheet_id: string;
    trigger_column: string;
    trigger_value: string;
    action_type: string;
    action_config: Record<string, unknown>;
    enabled: boolean;
}

/* ── Query Keys ───────────────────────────────────────── */
/*
 * Centralized query keys prevent typos and make invalidation reliable.
 * Pattern: [entity, ...identifiers]
 */

export const queryKeys = {
    workspaces: ["workspaces"] as const,
    sheets: (workspaceId: string) => ["sheets", workspaceId] as const,
    sheet: (sheetId: string) => ["sheet", sheetId] as const,
    rows: (sheetId: string) => ["rows", sheetId] as const,
    agentRules: (sheetId: string) => ["agentRules", sheetId] as const,
};

/* ── Workspace Hooks ──────────────────────────────────── */

export function useWorkspaces() {
    return useQuery({
        queryKey: queryKeys.workspaces,
        queryFn: () => api.get<WorkspaceResponse[]>("/workspaces"),
    });
}

export function useCreateWorkspace() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (name: string) =>
            api.post<WorkspaceResponse>("/workspaces", { name }),
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.workspaces }),
    });
}

/* ── Sheet Hooks ──────────────────────────────────────── */

export function useSheet(sheetId: string | null) {
    return useQuery({
        queryKey: queryKeys.sheet(sheetId ?? ""),
        queryFn: () => api.get<SheetResponse>(`/sheets/${sheetId}`),
        enabled: !!sheetId,
    });
}

/* ── Row Hooks ────────────────────────────────────────── */

export function useRows(sheetId: string | null) {
    return useQuery({
        queryKey: queryKeys.rows(sheetId ?? ""),
        queryFn: () => api.get<RowResponse[]>(`/sheets/${sheetId}/rows`),
        enabled: !!sheetId,
    });
}

export function useCreateRow(sheetId: string) {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: Record<string, string>) =>
            api.post<RowResponse>(`/sheets/${sheetId}/rows`, { data }),
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.rows(sheetId) }),
    });
}

/**
 * useMutateRow — PATCH a single row with OPTIMISTIC UPDATE
 *
 * ALGORITHM:
 *   1. onMutate: snapshot current cache, apply optimistic update
 *   2. API call runs in background
 *   3. onError: rollback to snapshot
 *   4. onSettled: invalidate to ensure server truth wins
 */
export function useMutateRow(sheetId: string) {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({
            rowId,
            data,
        }: {
            rowId: string;
            data: Record<string, string>;
        }) => api.patch<RowResponse>(`/rows/${rowId}`, { data }),

        onMutate: async ({ rowId, data }) => {
            // Cancel in-flight queries so they don't overwrite our optimistic update
            await qc.cancelQueries({ queryKey: queryKeys.rows(sheetId) });

            // Snapshot current state for rollback
            const previous = qc.getQueryData<RowResponse[]>(queryKeys.rows(sheetId));

            // Optimistically update the cache
            qc.setQueryData<RowResponse[]>(queryKeys.rows(sheetId), (old) =>
                old?.map((row) =>
                    row.id === rowId ? { ...row, data: { ...row.data, ...data } } : row,
                ),
            );

            return { previous };
        },

        onError: (_err, _vars, context) => {
            // Rollback on error
            if (context?.previous) {
                qc.setQueryData(queryKeys.rows(sheetId), context.previous);
            }
        },

        onSettled: () => {
            // Always refetch to ensure server truth
            qc.invalidateQueries({ queryKey: queryKeys.rows(sheetId) });
        },
    });
}

export function useDeleteRow(sheetId: string) {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (rowId: string) => api.delete(`/rows/${rowId}`),
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.rows(sheetId) }),
    });
}

export function useImportCSV(sheetId: string) {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (file: File) => {
            const fd = new FormData();
            fd.append("file", file);
            return api.upload<RowResponse[]>(`/sheets/${sheetId}/import-csv`, fd);
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.rows(sheetId) }),
    });
}

/* ── Agent Rule Hooks ─────────────────────────────────── */

export function useAgentRules(sheetId: string | null) {
    return useQuery({
        queryKey: queryKeys.agentRules(sheetId ?? ""),
        queryFn: () =>
            api.get<AgentRuleResponse[]>(`/agent-rules?sheet_id=${sheetId}`),
        enabled: !!sheetId,
    });
}

export function useToggleRule() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ ruleId, enabled }: { ruleId: string; enabled: boolean }) =>
            api.patch<AgentRuleResponse>(`/agent-rules/${ruleId}`, { enabled }),
        onSuccess: (data) => {
            qc.invalidateQueries({
                queryKey: queryKeys.agentRules(data.sheet_id),
            });
        },
    });
}
