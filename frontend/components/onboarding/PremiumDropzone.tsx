"use client";

import { useCallback, useState } from "react";
import { UploadCloud } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
    onFileSelect: (file: File) => void;
    onError: (error: string) => void;
}

export function PremiumDropzone({ onFileSelect, onError }: Props) {
    const [isDragging, setIsDragging] = useState(false);

    const validateAndSelect = (file: File) => {
        const validTypes = [
            'application/pdf', 
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        
        if (!validTypes.includes(file.type)) {
            onError("Invalid format. Please upload a PDF or DOCX.");
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            onError("File is too large. Maximum size is 5MB.");
            return;
        }

        onFileSelect(file);
    };

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
        else if (e.type === "dragleave") setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) validateAndSelect(file);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <motion.div
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
                group relative flex flex-col items-center justify-center w-full min-h-[300px] p-10 
                rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer
                overflow-hidden bg-background
                ${isDragging 
                    ? "border-primary bg-primary/5 shadow-soft" 
                    : "border-border hover:border-primary/40 hover:bg-accent/10"}
            `}
        >
            <div className="relative z-10 flex flex-col items-center text-center">
                <div className={`
                    p-4 rounded-2xl mb-6 transition-colors duration-300
                    ${isDragging ? "bg-primary/10 text-primary" : "bg-surface border border-border text-charcoal/50 group-hover:text-primary"}
                `}>
                    <UploadCloud className="w-8 h-8" />
                </div>
                
                <h3 className="text-xl font-bold text-charcoal mb-2 tracking-tight">
                    Select a document to upload
                </h3>
                <p className="text-base text-charcoal/60 mb-8">
                    or drag and drop it here
                </p>

                <label className="relative z-20 px-8 py-3 rounded-xl bg-surface border border-border hover:bg-accent/30 text-base font-semibold text-charcoal transition-colors cursor-pointer shadow-sm">
                    Browse Files
                    <input 
                        type="file" 
                        className="hidden" 
                        accept=".pdf,.doc,.docx"
                        onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) validateAndSelect(file);
                        }}
                    />
                </label>
                <p className="mt-6 text-xs font-medium text-charcoal/40 uppercase tracking-widest">
                    PDF, DOC up to 5MB
                </p>
            </div>
        </motion.div>
    );
}