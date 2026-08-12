"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Terminal, CheckCircle2 } from "lucide-react";

const logs = [
    "Initializing parsing engine...",
    "Extracting document structure...",
    "Mapping professional timeline...",
    "Normalizing technical skills...",
    "Generating candidate schema..."
];

export function ExtractionTerminal() {
    const [currentLog, setCurrentLog] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentLog((prev) => (prev < logs.length - 1 ? prev + 1 : prev));
        }, 1500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full rounded-2xl border border-border bg-background shadow-soft overflow-hidden">
            <div className="flex items-center gap-2 px-5 py-4 border-b border-border bg-surface">
                <Terminal className="w-4 h-4 text-primary" />
                <span className="text-sm font-semibold text-charcoal font-mono">system.process()</span>
            </div>
            
            <div className="p-6 font-mono text-sm h-[260px] flex flex-col justify-end space-y-3 bg-background">
                {logs.map((log, index) => {
                    if (index > currentLog) return null;
                    const isLast = index === currentLog;
                    
                    return (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`flex items-start gap-3 ${isLast ? 'text-charcoal' : 'text-charcoal/40'}`}
                        >
                            <span className="shrink-0 mt-0.5">
                                {isLast ? (
                                    <span className="w-4 h-4 rounded-full border-2 border-primary/30 border-t-primary animate-spin block" />
                                ) : (
                                    <CheckCircle2 className="w-4 h-4 text-primary" />
                                )}
                            </span>
                            <span className="font-medium">{log}</span>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}