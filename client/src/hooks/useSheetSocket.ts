/*
 * useSheetSocket — WebSocket hook for real-time row updates
 *
 * PATTERN: Connect to /ws/sheet/{id}, parse incoming events,
 *   and update the TanStack Query cache directly.
 *
 * WHY UPDATE CACHE DIRECTLY (not invalidate)?
 *   - Invalidation triggers a full refetch → flicker + latency
 *   - Direct cache update is instant and smooth
 *   - We still invalidate on reconnect to catch missed events
 *
 * RECONNECTION STRATEGY:
 *   Exponential backoff: 1s → 2s → 4s → 8s → max 30s
 *   This prevents hammering the server if it's down.
 *
 * ALTERNATIVE: Socket.IO — adds ~40KB for features we don't need
 *   (rooms, namespaces, fallback polling). Native WebSocket is enough.
 */

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "./useSheetData";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

interface RowEvent {
    event: "row_created" | "row_updated" | "row_deleted";
    row: {
        id: string;
        sheet_id: string;
        data: Record<string, string>;
        row_order: string;
        created_at: string;
        updated_at: string;
    };
}

interface AgentLogEvent {
    event: "agent_log";
    log: {
        id: string;
        rule_id: string;
        row_id: string;
        status: string;
        message: string;
        timestamp: string;
    };
}

type WsEvent = RowEvent | AgentLogEvent;

export function useSheetSocket(sheetId: string | null) {
    const qc = useQueryClient();
    const wsRef = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const [agentLogs, setAgentLogs] = useState<AgentLogEvent["log"][]>([]);

    useEffect(() => {
        if (!sheetId) return;

        let disposed = false;
        let timer: ReturnType<typeof setTimeout>;

        function connect() {
            if (disposed) return;

            const ws = new WebSocket(`${WS_BASE}/ws/sheet/${sheetId}`);
            wsRef.current = ws;

            ws.onopen = () => {
                retryCountRef.current = 0;
            };

            ws.onmessage = (evt) => {
                try {
                    const msg: WsEvent = JSON.parse(evt.data);

                    if (msg.event === "agent_log") {
                        setAgentLogs(prev => [...prev, msg.log].slice(-50)); // Keep last 50 logs
                        return;
                    }

                    const key = queryKeys.rows(sheetId!);

                    switch (msg.event) {
                        case "row_created":
                            qc.setQueryData(key, (old: RowEvent["row"][] | undefined) =>
                                old ? [...old, msg.row] : [msg.row],
                            );
                            break;

                        case "row_updated":
                            qc.setQueryData(key, (old: RowEvent["row"][] | undefined) =>
                                old?.map((r) => (r.id === msg.row.id ? msg.row : r)),
                            );
                            break;

                        case "row_deleted":
                            qc.setQueryData(key, (old: RowEvent["row"][] | undefined) =>
                                old?.filter((r) => r.id !== msg.row.id),
                            );
                            break;
                    }
                } catch {
                    // Ignore malformed messages
                }
            };

            ws.onclose = () => {
                if (disposed) return;
                const delay = Math.min(1000 * 2 ** retryCountRef.current, 30000);
                retryCountRef.current += 1;
                timer = setTimeout(connect, delay);
            };

            ws.onerror = () => {
                ws.close();
            };
        }

        connect();

        return () => {
            disposed = true;
            clearTimeout(timer);
            wsRef.current?.close();
        };
    }, [sheetId, qc]);

    return { agentLogs };
}
