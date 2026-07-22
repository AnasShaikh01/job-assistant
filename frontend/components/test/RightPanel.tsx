"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Briefcase } from "lucide-react";

import { authService } from "@/services/auth.service";
import { candidateService } from "@/services/candidate.service";

import { CandidateKnowledgeBase } from "@/types/candidate";

const emptyProfile: CandidateKnowledgeBase = {
    summary: "",
    skills: [],
    experience: [],
    education: [],
    projects: [],
    certifications: [],
    links: {
        github: null,
        linkedin: null,
        portfolio: null,
        other: [],
    },
};

type RightPanelProps = {
    job: any;
};

export default function RightPanel({ job }: RightPanelProps) {
    const { getToken } = useAuth();

    const [profile, setProfile] =
        useState<CandidateKnowledgeBase>(emptyProfile);

    const [loading, setLoading] = useState(false);
    const [loadingJob, setLoadingJob] = useState(false);

    const [error, setError] = useState("");

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            setLoading(true);
            setError("");

            const token = await getToken();

            if (!token) {
                setError("Unauthorized");
                return;
            }

            await authService.me(token);

            const candidateProfile =
                await candidateService.getProfile(token);

            setProfile(candidateProfile.ckb);

            console.log(candidateProfile.ckb);
        } catch (err) {
            console.error(err);
            setError("Failed to load profile.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">

            {/* Resume Module */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Resume Output
                    </CardTitle>
                </CardHeader>

                <CardContent>
                    {loading ? (
                        <p>Loading...</p>
                    ) : error ? (
                        <p className="text-red-500">{error}</p>
                    ) : (
                        <pre className="max-h-125 overflow-auto rounded-lg bg-gray-100 p-4 text-sm">
                            {JSON.stringify(profile, null, 2)}
                        </pre>
                    )}
                </CardContent>
            </Card>

            {/* Job Description Module */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Briefcase className="h-5 w-5" />
                        Job Description Output
                    </CardTitle>
                </CardHeader>

                <CardContent>
                    {loadingJob ? (
                        <p>Loading...</p>
                    ) : (
                        <pre className="max-h-125 overflow-auto rounded-lg bg-gray-100 p-4 text-sm">
                            {JSON.stringify(job, null, 2)}
                        </pre>
                    )}
                </CardContent>
            </Card>

        </div>
    );
}