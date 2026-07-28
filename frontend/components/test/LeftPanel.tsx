"use client";
import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Briefcase } from "lucide-react";
import {
    uploadJobDescription,
    parseJobFromUrl,
    parseJobFromText,
} from "@/services/jobs.service";

type LeftPanelProps = {
    setJob: (job: any) => void;
};

type JobTab = "pdf" | "url" | "text";

export default function LeftPanel({ setJob }: LeftPanelProps) {
    const { getToken } = useAuth();
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [uploadingResume, setUploadingResume] = useState(false);

    const [jobFile, setJobFile] = useState<File | null>(null);
    const [uploadingJob, setUploadingJob] = useState(false);

    const [jobTab, setJobTab] = useState<JobTab>("pdf");
    const [jobUrl, setJobUrl] = useState("");
    const [jobText, setJobText] = useState("");

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

    const handleJobUrlParse = async () => {
        if (!jobUrl.trim()) {
            alert("Please enter a Job URL.");
            return;
        }

        try {
            setUploadingJob(true);

            const token = await getToken();

            if (!token) {
                throw new Error("Not authenticated");
            }

            const response = await parseJobFromUrl(
                token,
                jobUrl
            );

            setJob(response.data);

            console.log(response.data);
        } catch (error) {
            console.error(error);

            const message =
                (error as any)?.response?.data?.message ||
                (error as any)?.response?.data?.detail ||
                "Failed to parse job URL.";

            alert(message);

        } finally {
            setUploadingJob(false);
        }
    };

    const handleJobTextParse = async () => {
        if (!jobText.trim()) {
            alert("Please enter a Job Description.");
            return;
        }

        try {
            setUploadingJob(true);

            const token = await getToken();

            if (!token) {
                throw new Error("Not authenticated");
            }

            const response = await parseJobFromText(
                token,
                jobText
            );

            setJob(response.data);

            console.log(response.data);
        } catch (error) {
            console.error(error);
            alert("Failed to parse job description.");
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

                    {/* Tabs */}
                    <div className="flex gap-2">
                        {(["pdf", "url", "text"] as JobTab[]).map((tab) => (
                            <Button
                                key={tab}
                                type="button"
                                variant={jobTab === tab ? "default" : "outline"}
                                size="sm"
                                onClick={() => setJobTab(tab)}
                                className="capitalize"
                            >
                                {tab}
                            </Button>
                        ))}
                    </div>

                    {/* PDF */}
                    {jobTab === "pdf" && (
                        <div className="space-y-4">
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
                                {uploadingJob
                                    ? "Uploading..."
                                    : "Upload Job Description"}
                            </Button>
                        </div>
                    )}

                    {/* URL */}
                    {jobTab === "url" && (
                        <div className="space-y-4">
                            <input
                                type="url"
                                placeholder="https://company.com/jobs/123"
                                value={jobUrl}
                                onChange={(e) => setJobUrl(e.target.value)}
                                className="w-full rounded-md border p-2"
                            />

                            <Button
                                className="w-full"
                                onClick={handleJobUrlParse}
                                disabled={uploadingJob}
                            >
                                {uploadingJob ? "Parsing..." : "Parse URL"}
                            </Button>
                        </div>
                    )}

                    {/* Text */}
                    {jobTab === "text" && (
                        <div className="space-y-4">
                            <textarea
                                rows={8}
                                placeholder="Paste the job description..."
                                value={jobText}
                                onChange={(e) => setJobText(e.target.value)}
                                className="w-full rounded-md border p-2"
                            />

                            <Button
                                className="w-full"
                                onClick={handleJobTextParse}
                                disabled={uploadingJob}
                            >
                                {uploadingJob ? "Parsing..." : "Parse Text"}
                            </Button>
                        </div>
                    )}

                </CardContent>
            </Card>

        </div>
    );
}