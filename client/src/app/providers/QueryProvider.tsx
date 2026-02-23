"use client";

/*
 * QueryProvider — Wraps the app in TanStack Query's QueryClientProvider
 *
 * WHY A SEPARATE COMPONENT?
 *   Next.js App Router requires "use client" for providers that use React
 *   context. The root layout.tsx is a server component, so we can't put
 *   QueryClientProvider there directly. This component bridges the gap.
 *
 * QUERY CLIENT CONFIG:
 *   - staleTime: 30s — data is "fresh" for 30s, no refetch on mount
 *   - retry: 1 — retry failed requests once (fast fail for dev)
 *   - refetchOnWindowFocus: true — refetch when user tabs back (default)
 *
 * ALTERNATIVE: Could use React Query's HydrationBoundary for SSR,
 *   but we're doing client-side data fetching for now (simpler, real-time).
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function QueryProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    // useState ensures one QueryClient per component lifecycle (not shared across requests)
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        staleTime: 30 * 1000, // 30 seconds
                        retry: 1,
                    },
                },
            }),
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}
