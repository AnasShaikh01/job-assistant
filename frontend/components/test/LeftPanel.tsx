"use client";
import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Briefcase } from "lucide-react";
import { uploadJobDescription } from "@/services/jobs.service";

type LeftPanelProps = {
    setJob: (job: any) => void;
};

export default function LeftPanel({ setJob }: LeftPanelProps) {
    const { getToken } = useAuth();
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [uploadingResume, setUploadingResume] = useState(false);

    const [jobFile, setJobFile] = useState<File | null>(null);
    const [uploadingJob, setUploadingJob] = useState(false);

    const handleResumeUpload = async () => {
        if (!resumeFile) {
            alert("Please select a resume.");
            return;
        }

        try {
            setUploadingResume(true);

            const token = await getToken();

            const formData = new FormData();
            formData.append("resume", resumeFile);

            const response = await api.post("/resume/upload", formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            console.log(response.data);
        } catch (error) {
            console.error(error);
            alert("Upload failed.");
        } finally {
            setUploadingResume(false);
        }
    };

    const handleJobUpload = async () => {
        if (!jobFile) {
            alert("Please select a Job Description.");
            return;
        }

        try {
            setUploadingJob(true);

            const token = await getToken();

            if (!token) {
                throw new Error("Not authenticated");
            }

            const response = await uploadJobDescription(
                token,
                jobFile
            );

            
            setJob(response.data);
            console.log(response.data);
        } catch (error) {
            console.error(error);
            alert("Upload failed.");
        } finally {
            setUploadingJob(false);
        }
    };

    return (
        <div className="space-y-6">

            {/* Resume Module */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Resume
                    </CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                    <input
                        type="file"
                        accept=".pdf,.doc,.docx"
                        onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
                    />

                    <Button
                        className="w-full"
                        onClick={handleResumeUpload}
                        disabled={uploadingResume}
                    >
                        {uploadingResume ? "Uploading..." : "Upload Resume"}
                    </Button>
                </CardContent>
            </Card>

            {/* Job Description Module */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Briefcase className="h-5 w-5" />
                        Job Description
                    </CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setJobFile(e.target.files?.[0] ?? null)}
                    />

                    <Button
                        className="w-full"
                        onClick={handleJobUpload}
                        disabled={uploadingJob}
                    >
                        {uploadingJob ? "Uploading..." : "Upload Job Description"}
                    </Button>
                </CardContent>
            </Card>

        </div>
    );
}