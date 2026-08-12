"use client";

import { useEffect } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { authService } from "@/services/auth.service";

export default function DashboardPage() {
    const { getToken, isLoaded: isAuthLoaded } = useAuth();
    const { user, isLoaded: isUserLoaded } = useUser();

    useEffect(() => {
        const initializeUser = async () => {
            // Prevent execution if Clerk is still loading or user is not logged in
            if (!isAuthLoaded || !isUserLoaded || !user) return;

            try {
                const token = await getToken();
                if (!token) return;

                const response = await authService.me(token);
                console.log("✅ Backend User:", response);
            } catch (error) {
                console.error("❌ Failed to sync user:", error);
            }
        };

        initializeUser();
    }, [getToken, isAuthLoaded, isUserLoaded, user]);

    // Optional: Return a sleek loading state while Clerk initializes
    if (!isUserLoaded) {
        return (
            <main className="min-h-screen bg-background p-10 flex items-center justify-center">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background p-10">
            <h1 className="text-3xl md:text-4xl font-bold text-charcoal tracking-tight mb-8">
                Dashboard
            </h1>

            <div className="bg-surface border border-border shadow-sm rounded-[24px] p-8 max-w-2xl">
                <p className="text-lg text-charcoal/80 mb-2">
                    Welcome back, <strong className="text-charcoal font-semibold">{user?.firstName}</strong>.
                </p>

                <p className="text-sm text-charcoal/60">
                    {user?.primaryEmailAddress?.emailAddress}
                </p>
            </div>
        </main>
    );
}