"use client";

import { motion } from "framer-motion";
import { Cpu, ShieldCheck, Zap, Sparkles } from "lucide-react";

export function OnboardingSidebar() {
    return (
        <div className="flex flex-col h-full p-8 md:p-10 z-10 w-full">
            <div className="flex items-center gap-3 mb-12">
                <div className="w-10 h-10 rounded-xl bg-accent/40 border border-accent/60 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-primary" />
                </div>
                <span className="text-xl font-bold tracking-tight text-charcoal">PrimeVex</span>
            </div>

            <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                className="flex-1 space-y-10"
            >
                <div className="space-y-8">
                    <Feature 
                        icon={Cpu}
                        title="Semantic Extraction"
                        description="Our engine understands the context of your achievements, not just keywords."
                    />
                    <Feature 
                        icon={Sparkles}
                        title="Instant Formatting"
                        description="Your data is structured perfectly for our specialized matching engines."
                    />
                    <Feature 
                        icon={ShieldCheck}
                        title="Enterprise Security"
                        description="Parsed in memory. Your PDF is never used to train public AI models."
                    />
                </div>
            </motion.div>

            <div className="mt-12 pt-8 border-t border-border">
                <div className="flex items-center gap-2 text-sm text-charcoal/60 font-medium">
                    <ShieldCheck className="w-4 h-4 text-primary" />
                    <span>256-bit SSL Encryption</span>
                </div>
            </div>
        </div>
    );
}

interface FeatureProps {
    icon: React.ElementType;
    title: string;
    description: string;
}

function Feature({ icon: Icon, title, description }: FeatureProps) {
    return (
        <div className="flex gap-4">
            <div className="shrink-0 mt-1">
                <Icon className="w-5 h-5 text-primary/80" />
            </div>
            <div>
                <h3 className="text-base font-semibold text-charcoal mb-1">{title}</h3>
                <p className="text-sm text-charcoal/70 leading-relaxed">{description}</p>
            </div>
        </div>
    );
}