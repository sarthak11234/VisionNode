import { useState } from 'react';
import { Send, Check, AlertTriangle, Edit2 } from 'lucide-react';
import { useAppStore, type Participant } from '../store/useAppStore';

export const ParticipantsTable = () => {
    const { participants, uploadStatus, updateParticipant } = useAppStore();
    const [editingId, setEditingId] = useState<number | null>(null);

    if (uploadStatus !== 'complete') return null;

    return (
        <div className="w-full max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">

            {/* Header Actions */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-display font-bold text-white">Participants</h2>
                    <p className="text-white/40 text-sm">Review detected details before sending invites.</p>
                </div>
                <button
                    className="group flex items-center gap-2 px-6 py-2.5 bg-accent text-black font-semibold rounded-lg hover:bg-accent/90 transition-all active:scale-95"
                    onClick={() => alert("Connecting to WhatsApp Automation...")}
                >
                    <span>Fire Invites</span>
                    <Send className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
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
                                    <td colSpan={6} className="p-8 text-center text-white/30">
                                        No participants detected. Try scanning again.
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
                    >
                        <Edit2 className="w-4 h-4" />
                    </button>
                )}
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
