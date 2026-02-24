const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Core fetch wrapper for the application.
 */
export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorBody = "Unknown error";
    try {
      errorBody = await response.text();
    } catch (e) {
      // Ignore text parse errors if no body
    }
    throw new Error(`API Error: ${response.status} - ${errorBody}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as any;
  }

  return response.json() as Promise<T>;
}

export const api = {
  // Workspaces
  getWorkspaces: () => fetchApi<any[]>("/workspaces"),
  createWorkspace: (data: { name: string; owner_id?: string }) => 
    fetchApi<any>("/workspaces", { method: "POST", body: JSON.stringify(data) }),
  
  // Sheets
  createSheet: (workspaceId: string, data: { name: string; column_schema: any[] }) => 
    fetchApi<any>(`/workspaces/${workspaceId}/sheets`, { method: "POST", body: JSON.stringify(data) }),
  getSheet: (sheetId: string) => fetchApi<any>(`/sheets/${sheetId}`),
  updateSheetColumns: (sheetId: string, data: any) => 
    fetchApi<any>(`/sheets/${sheetId}/columns`, { method: "PATCH", body: JSON.stringify(data) }),

  // Rows
  createRow: (sheetId: string, data: any) => 
    fetchApi<any>(`/sheets/${sheetId}/rows`, { method: "POST", body: JSON.stringify(data) }),
  updateRow: (rowId: string, data: { data: any }) => 
    fetchApi<any>(`/rows/${rowId}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteRow: (rowId: string) => 
    fetchApi<any>(`/rows/${rowId}`, { method: "DELETE" }),
  
  // Importer
  importCSV: async (sheetId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const url = `${API_BASE_URL}/sheets/${sheetId}/import-csv`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error(`CSV Import failed: ${response.statusText}`);
    return response.json();
  },

  // Agent Rules
  getAgentRules: (sheetId: string) => 
    fetchApi<any[]>(`/agent-rules?sheet_id=${sheetId}`),
  createAgentRule: (data: any) => 
    fetchApi<any>(`/agent-rules`, { method: "POST", body: JSON.stringify(data) }),
  updateAgentRule: (ruleId: string, data: any) => 
    fetchApi<any>(`/agent-rules/${ruleId}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteAgentRule: (ruleId: string) => 
    fetchApi<any>(`/agent-rules/${ruleId}`, { method: "DELETE" }),
};
