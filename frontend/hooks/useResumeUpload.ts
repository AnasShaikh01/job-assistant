"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { resumeService } from "@/services/resume.service";
import { ResumeUploadResponse } from "@/types/resume";

export function useResumeUpload() {
    const { getToken } = useAuth();
    
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [response, setResponse] = useState<ResumeUploadResponse | null>(null);

    const uploadResume = async (file: File) => {
        try {
            setUploading(true);
            setError(null);
            setResponse(null);

            // Strict Validation Boundary
            const validTypes = [
                'application/pdf', 
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ];
            
            if (!validTypes.includes(file.type)) {
                throw new Error("Invalid file format. Please upload a PDF, DOC, or DOCX.");
            }

            const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
            if (file.size > MAX_FILE_SIZE) {
                throw new Error("File exceeds the 5MB limit. Please upload a smaller document.");
            }

            const token = await getToken();
            if (!token) {
                throw new Error("Authentication token not found.");
            }

            const data = await resumeService.uploadResume(token, file);
            setResponse(data);
            return data;

        } catch (err) {
            console.error("Upload error:", err);
            const message = err instanceof Error ? err.message : "Failed to upload resume.";
            setError(message);
            throw err;
        } finally {
            setUploading(false);
        }
    };

    return {
        uploadResume,
        uploading,
        error,
        response
    };
}