import AppShell from "./components/AppShell";

export default function Home() {
  return (
    <AppShell>
      {/* Placeholder — TanStack Table will go here in Phase 2C */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          minHeight: 400,
          border: "1px dashed var(--border)",
          borderRadius: 8,
          color: "var(--text-tertiary)",
          fontFamily: "var(--font-mono)",
          fontSize: 14,
        }}
      >
        Spreadsheet view will render here
      </div>
    </AppShell>
  );
}

