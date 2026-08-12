"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

import { authService } from "@/services/auth.service";
import { candidateService } from "@/services/candidate.service";

import {
    CandidateKnowledgeBase,
    CandidateProfile,
} from "@/types/candidate";

import ProfileHero from "@/components/profile/ProfileHero";
import SummaryCard from "@/components/profile/SummaryCard";
import SkillsCard from "@/components/profile/SkillsCard";
import ExperienceCard from "@/components/profile/ExperienceCard";
import EducationCard from "@/components/profile/EducationCard";
import ProjectsCard from "@/components/profile/ProjectsCard";
import CertificationsCard from "@/components/profile/CertificationsCard";
import { Button } from "@/components/ui/button";

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

export default function ProfilePage() {
    const { getToken } = useAuth();

    const [candidateProfile, setCandidateProfile] =
        useState<CandidateProfile | null>(null);

    const [profile, setProfile] =
        useState<CandidateKnowledgeBase>(emptyProfile);

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    // Fix 1 & 2: Move loadProfile inside useEffect and add getToken as a dependency
    useEffect(() => {
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

                const fetchedProfile = await candidateService.getProfile(token);

                setCandidateProfile(fetchedProfile);
                setProfile(fetchedProfile.ckb);
            } catch (err) {
                console.error(err);
                setError("Failed to load profile.");
            } finally {
                setLoading(false);
            }
        };

        loadProfile();
    }, [getToken]);

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
            <div className="flex min-h-[60vh] items-center justify-center">
                <p className="text-muted-foreground animate-pulse">Loading profile...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <p className="text-danger font-medium">{error}</p>
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-4xl space-y-6 pb-20 pt-6">
            <ProfileHero lastUpdated={candidateProfile?.updatedAt} />

            <SummaryCard
                profile={profile}
                setProfile={setProfile}
            />

            <SkillsCard profile={profile} />

            <ExperienceCard profile={profile} />

            <EducationCard profile={profile} />

            <ProjectsCard profile={profile} />

            <CertificationsCard profile={profile} />

            <div className="flex justify-end pt-6 border-t border-border">
                <Button 
                    onClick={saveProfile} 
                    disabled={saving} 
                    className="w-full sm:w-auto"
                >
                    {saving ? "Saving..." : "Save Changes"}
                </Button>
            </div>
        </div>
    );
}