import { create } from 'zustand';

export interface Participant {
    name: string;
    phone: string;
    act: string;
    confidence?: number;
    status: 'pending' | 'sent' | 'failed';
    customMessage?: string;
}

interface AppState {
    participants: Participant[];
    uploadStatus: 'idle' | 'scanning' | 'complete' | 'error';
    agentStatus: 'connected' | 'disconnected';

    setParticipants: (data: Participant[]) => void;
    addParticipants: (data: Participant[]) => void;
    updateParticipant: (index: number, data: Partial<Participant>) => void;
    setUploadStatus: (status: AppState['uploadStatus']) => void;
    setAgentStatus: (status: AppState['agentStatus']) => void;
}

export const useAppStore = create<AppState>((set) => ({
    participants: [],
    uploadStatus: 'idle',
    agentStatus: 'connected', // We assume connected for now, can poll later

    setParticipants: (data) => set({ participants: data }),
    addParticipants: (data) => set((state) => ({ participants: [...state.participants, ...data] })),

    updateParticipant: (index, data) => set((state) => {
        const newParticipants = [...state.participants];
        newParticipants[index] = { ...newParticipants[index], ...data };
        return { participants: newParticipants };
    }),

    setUploadStatus: (status) => set({ uploadStatus: status }),
    setAgentStatus: (status) => set({ agentStatus: status }),
}));
