const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchWithMethod<T>(endpoint: string, method: string, body?: any): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  if (!response.ok) {
    const errorBody = await response.text().catch(() => "Unknown Error");
    throw new Error(`API Error: ${response.status} - ${errorBody}`);
  }
  if (response.status === 204) return null as any;
  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(endpoint: string) => fetchWithMethod<T>(endpoint, "GET"),
  post: <T>(endpoint: string, body?: any) => fetchWithMethod<T>(endpoint, "POST", body),
  patch: <T>(endpoint: string, body?: any) => fetchWithMethod<T>(endpoint, "PATCH", body),
  delete: <T>(endpoint: string) => fetchWithMethod<T>(endpoint, "DELETE"),
  upload: async <T>(endpoint: string, formData: FormData): Promise<T> => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const errorBody = await response.text().catch(() => "Unknown Error");
      throw new Error(`API Error: ${response.status} - ${errorBody}`);
    }
    return response.json() as Promise<T>;
  },
};
