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

            if (response.data && Array.isArray(response.data.participants)) {
                addParticipants(response.data.participants);
                setUploadStatus('complete');
            } else {
                console.error("Invalid response format:", response.data);
                setUploadStatus('error');
                alert("Failed to parse participants. Please try again or enter manually.");
            }
        } catch (error) {
            console.error(error);
            setUploadStatus('error');
            alert("Error uploading image. Make sure the backend is running.");
        }
    };

    const handleManualEntry = (e: React.MouseEvent) => {
        e.stopPropagation();
        setUploadStatus('complete'); // Go to table
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
                    <div className="flex flex-col items-center gap-4 py-8">
                        <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
                        <div className="text-center">
                            <p className="text-lg font-medium text-white">Scanning...</p>
                            <p className="text-sm text-white/50">Please wait while we read the image.</p>
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
                            <p className="text-sm text-white/40 mt-1 mb-4">
                                or click to browse (JPG, PNG)
                            </p>
                            <button
                                onClick={handleManualEntry}
                                className="text-sm text-accent hover:text-accent/80 underline decoration-dashed underline-offset-4 transition-colors z-20 relative"
                            >
                                Or enter details manually
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
