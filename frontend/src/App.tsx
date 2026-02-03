import { Header } from './components/Header';
import { Dropzone } from './components/Dropzone';
import { ParticipantsTable } from './components/ParticipantsTable';

function App() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-accent/5 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2 pointer-events-none" />

      <Header />

      <main className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-4xl mx-auto mb-12 text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold text-white mb-4 tracking-tight">
            Audition Automation <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-white/40">
              Powered by Local Vision
            </span>
          </h2>
          <p className="text-lg text-white/50 max-w-xl mx-auto">
            Upload a photo of the registration sheet. Our local AI agent will parse the details and prepare WhatsApp invites instantly.
          </p>
        </div>

        <Dropzone />

        <div className="mt-8">
          <ParticipantsTable />
        </div>
      </main>
    </div>
  );
}

// Simple Error Boundary implementation for function components
import { Component, type ErrorInfo, type ReactNode } from "react";

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(_: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center text-white">
          <h1 className="text-2xl font-bold text-red-500 mb-4">Something went wrong.</h1>
          <button
            className="px-4 py-2 bg-white/10 rounded hover:bg-white/20"
            onClick={() => window.location.reload()}
          >
            Reload App
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default function WrappedApp() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  )
}
