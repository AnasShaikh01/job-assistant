"use client";

import { useEffect } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { authService } from "@/services/auth.service";

export default function DashboardPage() {
    const { getToken } = useAuth();
    const { user } = useUser();

    useEffect(() => {
        const initializeUser = async () => {
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
    }, [getToken]);

    return (
        <main className="p-10">
            <h1 className="text-3xl font-bold">Dashboard 🎉</h1>

            <p className="mt-4">
                Welcome, <strong>{user?.firstName}</strong>
            </p>

            <p>{user?.primaryEmailAddress?.emailAddress}</p>
        </main>
    );
}