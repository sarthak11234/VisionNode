/*
 * API Client — Centralized fetch wrapper for the FastAPI backend
 *
 * WHY A CUSTOM CLIENT (not Axios, ky, or raw fetch)?
 *   - Zero dependency: reduces bundle size by ~15KB vs Axios
 *   - Type-safe: generic request<T>() returns typed responses
 *   - Base URL config: one place to change when deploying
 *   - Error normalization: all API errors become ApiError instances
 *
 * ALTERNATIVE: Axios (~15KB) — more features (interceptors, progress),
 *   but we don't need them yet. We can swap later if needed.
 *
 * BASE URL STRATEGY:
 *   - Dev: uses NEXT_PUBLIC_API_URL env var (defaults to http://localhost:8000)
 *   - Prod: set NEXT_PUBLIC_API_URL to the deployed backend URL
 *   - The /api/v1 prefix is baked in so callers just use relative paths
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_PREFIX = "/api/v1";

/* ── Error Class ──────────────────────────────────────── */

export class ApiError extends Error {
    constructor(
        public status: number,
        public detail: string,
    ) {
        super(detail);
        this.name = "ApiError";
    }
}

/* ── Core Request Function ────────────────────────────── */

async function request<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    const url = `${BASE_URL}${API_PREFIX}${path}`;

    const res = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
        ...options,
    });

    if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new ApiError(res.status, body.detail ?? res.statusText);
    }

    // 204 No Content
    if (res.status === 204) return undefined as T;

    return res.json();
}

/* ── Typed API Methods ────────────────────────────────── */

export const api = {
    get: <T>(path: string) => request<T>(path),

    post: <T>(path: string, body?: unknown) =>
        request<T>(path, {
            method: "POST",
            body: body ? JSON.stringify(body) : undefined,
        }),

    patch: <T>(path: string, body: unknown) =>
        request<T>(path, {
            method: "PATCH",
            body: JSON.stringify(body),
        }),

    delete: <T>(path: string) =>
        request<T>(path, { method: "DELETE" }),

    /** For file uploads (CSV import) — don't set Content-Type, let browser handle it */
    upload: <T>(path: string, formData: FormData) =>
        request<T>(path, {
            method: "POST",
            headers: {}, // override Content-Type so browser sets multipart boundary
            body: formData as unknown as BodyInit,
        }),
};
