import { useState } from 'react';
import axios from 'axios';
import { Send, Check, AlertTriangle, Edit2, Plus, MessageCircle } from 'lucide-react';
import { useAppStore, type Participant } from '../store/useAppStore';

export const ParticipantsTable = () => {
    const { participants, uploadStatus, updateParticipant, addParticipants } = useAppStore();
    const [editingId, setEditingId] = useState<number | null>(null);

    const handleFireInvites = async () => {
        if (participants.length === 0) return;
        if (!window.confirm(`Send invites to ${participants.length} people?`)) return;
        try {
            await axios.post('http://localhost:8000/invite', { participants });
            alert("All invites sent!");
        } catch (e) { alert("Error sending invites"); }
    };

    const sendIndividual = async (index: number, p: Participant) => {
        const msg = prompt(`Enter message for ${p.name}:`, p.customMessage || `Hey ${p.name}, join us!`);
        if (msg === null) return; // Cancelled

        // Update store with custom message
        updateParticipant(index, { customMessage: msg });

        try {
            // Send just this one
            await axios.post('http://localhost:8000/invite', {
                participants: [{ ...p, customMessage: msg }]
            });
            alert(`Message sent to ${p.name}!`);
            updateParticipant(index, { status: 'sent' });
        } catch (e) {
            alert("Failed to send message.");
        }
    };


    return (
        <div className="w-full max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">

            {/* Header Actions */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-display font-bold text-white">Participants</h2>
                    <p className="text-white/40 text-sm">Review detected details before sending invites.</p>
                </div>
                <div className="flex gap-3">
                    <button
                        className="flex items-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 text-white hover:bg-white/10 rounded-lg transition-colors text-sm font-medium"
                        onClick={() => addParticipants([{ name: '', phone: '', act: '', status: 'pending' }])}
                    >
                        <Plus className="w-4 h-4" />
                        Add Row
                    </button>
                    <button
                        className="px-4 py-2.5 bg-white/5 border border-white/10 text-white hover:bg-white/10 rounded-lg transition-colors text-sm font-medium"
                        onClick={() => useAppStore.getState().setUploadStatus('idle')}
                    >
                        + Scan Page
                    </button>
                    <button
                        className="group flex items-center gap-2 px-6 py-2.5 bg-accent text-black font-semibold rounded-lg hover:bg-accent/90 transition-all active:scale-95"
                        onClick={handleFireInvites}
                    >
                        <span>Fire Invites</span>
                        <Send className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </div>

            {/* Table Card */}
            <div className="bg-surface border border-white/5 rounded-xl overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white/5 bg-white/[0.02]">
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider">#</th>
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider">Name</th>
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider">Phone (+91)</th>
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider">Act</th>
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider">Status</th>
                                <th className="p-4 text-xs font-mono text-white/40 uppercase tracking-wider text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {participants.map((p, idx) => (
                                <EditableRow
                                    key={idx}
                                    index={idx}
                                    data={p}
                                    isEditing={editingId === idx}
                                    onEdit={() => setEditingId(idx)}
                                    onSave={() => setEditingId(null)}
                                    onChange={(field, val) => updateParticipant(idx, { [field]: val })}
                                />
                            ))}
                            {participants.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="p-12 text-center">
                                        <p className="text-white/30 mb-4">No participants yet.</p>
                                        <button
                                            onClick={() => addParticipants([{ name: '', phone: '', act: '', status: 'pending' }])}
                                            className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-accent rounded-md transition-colors text-sm"
                                        >
                                            <Plus className="w-4 h-4" />
                                            Add Manually
                                        </button>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const EditableRow = ({
    index,
    data,
    isEditing,
    onEdit,
    onSave,
    onChange
}: {
    index: number;
    data: Participant;
    isEditing: boolean;
    onEdit: () => void;
    onSave: () => void;
    onChange: (field: keyof Participant, val: string) => void;
}) => {
    const isSuspicious = data.phone.includes("??") || data.phone.length !== 10;

    return (
        <tr className={`group transition-colors ${isEditing ? 'bg-white/5' : 'hover:bg-white/[0.02]'}`}>
            <td className="p-4 text-white/30 font-mono text-sm">{index + 1}</td>

            {/* Name */}
            <td className="p-4">
                {isEditing ? (
                    <input
                        value={data.name}
                        onChange={(e) => onChange('name', e.target.value)}
                        className="bg-black/40 border border-white/10 rounded px-2 py-1 text-white text-sm focus:border-accent outline-none w-full"
                        autoFocus
                    />
                ) : (
                    <span className="font-medium text-white">{data.name}</span>
                )}
            </td>

            {/* Phone */}
            <td className="p-4">
                {isEditing ? (
                    <input
                        value={data.phone}
                        onChange={(e) => onChange('phone', e.target.value)}
                        className="bg-black/40 border border-white/10 rounded px-2 py-1 text-white font-mono text-sm focus:border-accent outline-none w-full"
                    />
                ) : (
                    <div className="flex items-center gap-2">
                        <span className={`font-mono text-sm ${isSuspicious ? 'text-warning underline decoration-dashed' : 'text-white/80'}`}>
                            {data.phone}
                        </span>
                        {isSuspicious && (
                            <AlertTriangle className="w-3 h-3 text-warning" />
                        )}
                    </div>
                )}
            </td>

            {/* Act */}
            <td className="p-4">
                {isEditing ? (
                    <input
                        value={data.act}
                        onChange={(e) => onChange('act', e.target.value)}
                        className="bg-black/40 border border-white/10 rounded px-2 py-1 text-white text-sm focus:border-accent outline-none w-full"
                    />
                ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-white/5 text-white/60">
                        {data.act}
                    </span>
                )}
            </td>

            {/* Status */}
            <td className="p-4">
                <StatusBadge status={data.status} />
            </td>

            {/* Actions */}
            <td className="p-4 text-right">
                {isEditing ? (
                    <button
                        onClick={onSave}
                        className="p-1.5 rounded-md bg-success/10 text-success hover:bg-success/20 transition-colors"
                    >
                        <Check className="w-4 h-4" />
                    </button>
                ) : (
                    <button
                        onClick={onEdit}
                        className="p-1.5 rounded-md text-white/40 hover:text-white hover:bg-white/5 transition-colors opacity-0 group-hover:opacity-100"
                        title="Edit Details"
                    >
                        <Edit2 className="w-4 h-4" />
                    </button>
                )}
                <button
                    onClick={() => (window as any).sendIndividual(index, data)}
                    className="p-1.5 rounded-md text-accent/60 hover:text-accent hover:bg-accent/10 transition-colors opacity-0 group-hover:opacity-100 ml-1"
                    title="Send Custom Message"
                >
                    <MessageCircle className="w-4 h-4" />
                </button>
            </td>
        </tr>
    );
};

const StatusBadge = ({ status }: { status: Participant['status'] }) => {
    const styles = {
        pending: 'bg-white/5 text-white/40',
        sent: 'bg-success/10 text-success',
        failed: 'bg-red-500/10 text-red-500',
    };

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
            {status === 'pending' && <span className="w-1.5 h-1.5 rounded-full bg-white/40 mr-1.5" />}
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};
