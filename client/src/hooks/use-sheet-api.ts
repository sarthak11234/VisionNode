import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";

// --- Queries ---

export function useWorkspaces() {
    return useQuery({
        queryKey: ["workspaces"],
        queryFn: () => api.getWorkspaces(),
    });
}

export function useSheet(sheetId: string) {
    return useQuery({
        queryKey: ["sheet", sheetId],
        queryFn: () => api.getSheet(sheetId),
        enabled: !!sheetId,
    });
}

export function useAgentRules(sheetId: string) {
    return useQuery({
        queryKey: ["agentRules", sheetId],
        queryFn: () => api.getAgentRules(sheetId),
        enabled: !!sheetId,
    });
}

// --- Mutations ---

export function useMutateRow(sheetId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ rowId, data }: { rowId: string; data: any }) =>
            api.updateRow(rowId, { data }),
        onSuccess: () => {
            // Invalidate the sheet query to refetch the updated rows
            queryClient.invalidateQueries({ queryKey: ["sheet", sheetId] });
        },
    });
}

export function useCreateRow(sheetId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: any) => api.createRow(sheetId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["sheet", sheetId] });
        },
    });
}

export function useDeleteRow(sheetId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (rowId: string) => api.deleteRow(rowId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["sheet", sheetId] });
        },
    });
}

export function useImportCSV(sheetId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (file: File) => api.importCSV(sheetId, file),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["sheet", sheetId] });
        },
    });
}
