"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api } from "@/lib/api";

export default function ResumeUploadCard() {
    const { getToken } = useAuth();

    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a resume.");
            return;
        }

        try {
            setUploading(true);

            const token = await getToken();

            const formData = new FormData();
            formData.append("resume", file);

            const response = await api.post("/resume/upload", formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            console.log(response.data);
            alert("Resume uploaded successfully!");
        } catch (error) {
            console.error(error);
            alert("Upload failed.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="rounded-xl p-6 space-y-4">
            <h2 className="text-xl font-semibold">Upload Resume</h2>

            <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />

            <button
                onClick={handleUpload}
                disabled={uploading}
                className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
            >
                {uploading ? "Uploading..." : "Upload Resume"}
            </button>
        </div>
    );
}