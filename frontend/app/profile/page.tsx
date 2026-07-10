"use client";

import ProfileHeader from "@/components/profile/ProfileHeader";
import SummarySection from "@/components/profile/SummarySection";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

import { authService } from "@/services/auth.service";
import { candidateService } from "@/services/candidate.service";


import {
    CandidateKnowledgeBase,
    CandidateProfile,
} from "@/types/candidate";
import SkillsSection from "@/components/profile/SkillsSection";
import ExperienceSection from "@/components/profile/ExperienceSection";
import EducationSection from "@/components/profile/EducationSection";
import ProjectsSection from "@/components/profile/ProjectsSection";
import CertificationsSection from "@/components/profile/CertificationsSection";

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

const emptyExperience = {
    company: "",
    role: "",
    start_date: "",
    end_date: "",
    description: "",
    technologies: [],
};

export default function ProfilePage() {
    const { getToken } = useAuth();

    const [candidateProfile, setCandidateProfile] =
        useState<CandidateProfile | null>(null);

    const [profile, setProfile] =
        useState<CandidateKnowledgeBase>(emptyProfile);

    const [loading, setLoading] = useState(true);

    const [saving, setSaving] = useState(false);

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

            // Ensure the user exists in our database
            await authService.me(token);

            const candidateProfile =
                await candidateService.getProfile(token);

            setCandidateProfile(candidateProfile);
            setProfile(candidateProfile.ckb);
        } catch (err) {
            console.error(err);
            setError("Failed to load profile.");
        } finally {
            setLoading(false);
        }
    };

    const saveProfile = async () => {
        try {
            setSaving(true);

            const token = await getToken();

            if (!token) return;

            await candidateService.updateProfile(
                token,
                profile
            );

            alert("Profile updated successfully!");
        } catch (err) {
            console.error(err);
            alert("Failed to update profile.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <main className="max-w-5xl mx-auto py-10 px-6">
                <h1 className="text-2xl font-bold">Loading profile...</h1>
            </main>
        );
    }

    if (error) {
        return (
            <main className="max-w-5xl mx-auto py-10 px-6">
                <h1 className="text-2xl font-bold text-red-500">
                    {error}
                </h1>
            </main>
        );
    }

    return (
        <main className="max-w-5xl mx-auto py-10 px-6 space-y-8">
            <ProfileHeader
                lastUpdated={candidateProfile?.updatedAt}
            />

            <SummarySection
                profile={profile}
                setProfile={setProfile}
            />

            <SkillsSection
                profile={profile}
            />

            <ExperienceSection
                profile={profile}
            />

            <EducationSection
                profile={profile}
            />

            <ProjectsSection
                profile={profile}
            />

            <CertificationsSection
                profile={profile}
            />

        </main>
    );
}