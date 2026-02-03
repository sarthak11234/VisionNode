import { useState, useCallback } from 'react';
import { Upload } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import axios from 'axios';

export const Dropzone = () => {
    const [isDragActive, setIsDragActive] = useState(false);
    const { setUploadStatus, uploadStatus, addParticipants } = useAppStore();

    const handleFile = async (file: File) => {
        if (!file.type.startsWith('image/')) return;

        setUploadStatus('scanning');

        const formData = new FormData();
        formData.append('file', file);

        try {
            // In production, use env var. For local dev, proxy or direct URL.
            // We assume proxy is not set up, so direct URL.
            const response = await axios.post('http://localhost:8000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            addParticipants(response.data.participants);
            setUploadStatus('complete');
        } catch (error) {
            console.error(error);
            setUploadStatus('error');
        }
    };

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    if (uploadStatus === 'complete') return null; // Hide after successful upload to show table

    return (
        <div
            className={`relative w-full max-w-2xl mx-auto mt-12 mb-8 transition-all duration-300 ${isDragActive ? 'scale-[1.02]' : ''
                }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragActive(true); }}
            onDragLeave={() => setIsDragActive(false)}
            onDrop={onDrop}
        >
            <div
                className={`
          flex flex-col items-center justify-center h-64 border-2 border-dashed rounded-2xl 
          transition-colors cursor-pointer bg-surface/50 backdrop-blur-sm
          ${isDragActive ? 'border-accent bg-accent/5' : 'border-white/10 hover:border-white/20'}
          ${uploadStatus === 'scanning' ? 'pointer-events-none' : ''}
        `}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={(e) => e.target.files && handleFile(e.target.files[0])}
                    disabled={uploadStatus === 'scanning'}
                />

                {uploadStatus === 'scanning' ? (
                    <div className="flex flex-col items-center gap-4 z-10">
                        <div className="relative w-16 h-16 flex items-center justify-center">
                            <div className="absolute inset-0 border-t-2 border-accent rounded-full animate-spin" />
                            <div className="absolute inset-2 border-r-2 border-accent/50 rounded-full animate-spin reverse" />
                            <span className="text-2xl">👁️</span>
                        </div>
                        <div className="text-center">
                            <p className="text-lg font-medium text-white">Analyzing Audition Sheet...</p>
                            <p className="text-sm text-white/40">Extracting names & numbers</p>
                        </div>
                        {/* Scanning Beam Effect */}
                        <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
                            <div className="absolute w-full h-1 bg-accent/50 shadow-[0_0_20px_rgba(0,209,255,0.8)] animate-scan" />
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-4 text-center p-6">
                        <div className={`p-4 rounded-full ${isDragActive ? 'bg-accent/20' : 'bg-white/5'}`}>
                            <Upload className={`w-8 h-8 ${isDragActive ? 'text-accent' : 'text-white/40'}`} />
                        </div>
                        <div>
                            <p className="text-lg font-medium text-white">
                                Drag & drop your audition sheet
                            </p>
                            <p className="text-sm text-white/40 mt-1">
                                or click to browse (JPG, PNG)
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
