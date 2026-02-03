import { Radio } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export const Header = () => {
    const { agentStatus } = useAppStore();

    return (
        <header className="w-full border-b border-white/5 bg-[#0F0F12]/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                {/* Brand */}
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center">
                        <Radio className="w-4 h-4 text-accent animate-pulse" />
                    </div>
                    <h1 className="text-lg font-display font-semibold tracking-tight text-white">
                        Vision<span className="text-accent">Node</span>
                        <span className="ml-2 text-xs font-mono text-white/40 px-2 py-0.5 rounded-full bg-white/5">v2.0</span>
                    </h1>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1A1A1E] border border-white/5">
                        <div className={`w-2 h-2 rounded-full ${agentStatus === 'connected' ? 'bg-success shadow-[0_0_8px_rgba(0,255,148,0.5)]' : 'bg-red-500'}`} />
                        <span className="text-xs font-mono text-white/60">
                            OLLAMA: {agentStatus === 'connected' ? 'ONLINE' : 'OFFLINE'}
                        </span>
                    </div>
                </div>
            </div>
        </header>
    );
};
