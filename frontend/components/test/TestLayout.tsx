"use client";

import { useState } from "react";

import Header from "./Header";
import LeftPanel from "./LeftPanel";
import RightPanel from "./RightPanel";

export default function TestLayout() {
    const [job, setJob] = useState<any>(null);

    const handleReset = () => {
        window.location.reload();
    };

    return (
        <div className="min-h-screen bg-muted/30">
            <div className="mx-auto max-w-7xl space-y-6 p-6">

                <Header onReset={handleReset} />

                <div className="grid grid-cols-1 gap-6 lg:grid-cols-10">

                    <div className="lg:col-span-3">
                        <LeftPanel setJob={setJob} />
                    </div>

                    <div className="lg:col-span-7">
                        <RightPanel job={job} />
                    </div>

                </div>

            </div>
        </div>
    );
}