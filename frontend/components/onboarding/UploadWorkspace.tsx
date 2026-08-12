"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, X } from "lucide-react";
import { PremiumDropzone } from "./PremiumDropzone";
import { ExtractionTerminal } from "./ExtractionTerminal";
import { useResumeUpload } from "@/hooks/useResumeUpload";

export function UploadWorkspace() {
    const router = useRouter();
    const { uploadResume, uploading, error: hookError } = useResumeUpload();
    
    const [file, setFile] = useState<File | null>(null);
    const [localError, setLocalError] = useState<string | null>(null);

    const handleFileSelect = (selectedFile: File) => {
        setLocalError(null);
        setFile(selectedFile);
    };

    const handleProcess = async () => {
        if (!file) return;
        setLocalError(null);
        
        try {
            await uploadResume(file);
            router.push("/profile");
        } catch {
            // Handled via hookError
        }
    };

    const displayError = localError || hookError;

    return (
        <div className="w-full flex flex-col justify-center min-h-[400px]">
            <div className="mb-8">
                <h2 className="text-2xl md:text-3xl font-bold text-charcoal mb-2 tracking-tight">Upload Resume</h2>
                <p className="text-charcoal/70 text-base">Select a PDF or DOCX file to begin extraction.</p>
            </div>

            <AnimatePresence mode="wait">
                {uploading ? (
                    <motion.div
                        key="terminal"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <ExtractionTerminal />
                    </motion.div>
                ) : (
                    <motion.div
                        key="upload-form"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-6"
                    >
                        {!file ? (
                            <PremiumDropzone 
                                onFileSelect={handleFileSelect} 
                                onError={setLocalError} 
                            />
                        ) : (
                            <div className="p-4 rounded-xl border border-border bg-background flex items-center justify-between shadow-sm">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-accent/40 border border-accent flex items-center justify-center">
                                        <FileText className="w-6 h-6 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-charcoal truncate max-w-[200px] sm:max-w-[300px]">{file.name}</p>
                                        <p className="text-xs text-charcoal/60 font-medium">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                </div>
                                <button 
                                    onClick={() => setFile(null)}
                                    className="p-2 rounded-lg text-charcoal/50 hover:text-charcoal hover:bg-surface transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        )}

                        {displayError && (
                            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm font-medium shadow-sm">
                                {displayError}
                            </div>
                        )}

                        <div className="flex justify-end pt-4">
                            <button
                                onClick={handleProcess}
                                disabled={!file}
                                className={`
                                    h-12 px-8 rounded-xl text-base font-semibold transition-all duration-300
                                    ${file 
                                        ? "bg-primary text-white shadow-soft hover:shadow-lift hover:bg-primary/90" 
                                        : "bg-surface border border-border text-charcoal/40 cursor-not-allowed"
                                    }
                                `}
                            >
                                Generate Profile
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}