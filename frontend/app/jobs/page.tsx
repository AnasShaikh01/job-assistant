"use client";

import { useAuth } from "@clerk/nextjs";
import { useState } from "react";
import { uploadJobDescription } from "@/services/jobs.service";

type Tab = "text" | "pdf" | "url";

export default function JobsPage() {
    const [activeTab, setActiveTab] = useState<Tab>("pdf");
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<any>(null);

    const { getToken } = useAuth();

    const handleUpload = async () => {
        if (!file) return;

        try {
            setLoading(true);

            const token = await getToken();

            if (!token) {
                throw new Error("Not authenticated");
            }

            const response = await uploadJobDescription(
                token,
                file
            );

            setResult(response);
        } finally {
            setLoading(false);
        }
    };

    const tabs: Tab[] = ["text", "pdf", "url"];

    return (
        <div className="mx-auto max-w-5xl p-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    Job Description
                </h1>
                <p className="mt-2 text-gray-600">
                    Parse a job description from text, PDF, or a job posting
                    URL.
                </p>
            </div>

            {/* Tabs */}
            <div className="mb-6 flex gap-3">
                {tabs.map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`rounded-lg border px-5 py-2 font-medium capitalize transition ${activeTab === tab
                                ? "border-blue-600 bg-blue-600 text-white"
                                : "border-gray-300 bg-white text-gray-700 hover:bg-gray-100"
                            }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Card */}
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                {activeTab === "text" && (
                    <div className="space-y-4">
                        <textarea
                            rows={12}
                            placeholder="Paste the job description..."
                            className="w-full rounded-lg border border-gray-300 p-3 focus:border-blue-500 focus:outline-none"
                        />

                        <button
                            disabled
                            className="rounded-lg bg-gray-300 px-5 py-2 text-white"
                        >
                            Parse Text (Coming Soon)
                        </button>
                    </div>
                )}

                {activeTab === "pdf" && (
                    <div className="space-y-6">
                        <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-10 transition hover:border-blue-500 hover:bg-blue-50">
                            <span className="text-lg font-medium text-gray-700">
                                Click to upload a Job Description PDF
                            </span>

                            <span className="mt-1 text-sm text-gray-500">
                                PDF files only
                            </span>

                            <input
                                type="file"
                                accept=".pdf"
                                className="hidden"
                                onChange={(e) =>
                                    setFile(e.target.files?.[0] || null)
                                }
                            />
                        </label>

                        {file && (
                            <div className="rounded-lg border bg-gray-50 p-3 text-sm text-gray-700">
                                📄 {file.name}
                            </div>
                        )}

                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className="rounded-lg bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
                        >
                            {loading ? "Parsing..." : "Upload & Parse"}
                        </button>
                    </div>
                )}

                {activeTab === "url" && (
                    <div className="space-y-4">
                        <input
                            type="text"
                            placeholder="https://company.com/careers/job"
                            className="w-full rounded-lg border border-gray-300 p-3 focus:border-blue-500 focus:outline-none"
                        />

                        <button
                            disabled
                            className="rounded-lg bg-gray-300 px-5 py-2 text-white"
                        >
                            Parse URL (Coming Soon)
                        </button>
                    </div>
                )}
            </div>

            {result && (
                <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h2 className="mb-4 text-xl font-semibold">
                        Parsed Output
                    </h2>

                    <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm text-green-400">
                        {JSON.stringify(result, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
}