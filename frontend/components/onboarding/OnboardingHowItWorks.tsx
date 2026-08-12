"use client";

import { motion, Variants } from "framer-motion";
import { FileUp, Sparkles, Database } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function OnboardingHowItWorks() {
    const steps = [
        {
            icon: <FileUp className="w-6 h-6" />,
            title: "Secure Document Ingestion",
            description: "Upload your existing PDF or DOCX. Our secure pipeline encrypts your file in transit and memory, ensuring complete privacy.",
        },
        {
            icon: <Sparkles className="w-6 h-6" />,
            title: "Semantic AI Extraction",
            description: "Our vision-capable AI reads your resume like a senior recruiter, understanding context, impact metrics, and trajectory.",
        },
        {
            icon: <Database className="w-6 h-6" />,
            title: "Knowledge Base Generation",
            description: "Your static document is converted into a structured, dynamic Candidate Profile ready for tailored applications.",
        }
    ];

    const containerVariants: Variants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.15 }
        }
    };

    const itemVariants: Variants = {
        hidden: { opacity: 0, y: 20 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.6, ease: "easeOut" }
        }
    };

    return (
        <section className="py-24 md:py-32 bg-background border-y border-border">
            <div className="max-w-7xl mx-auto px-6">
                
                <div className="flex flex-col lg:flex-row lg:items-end justify-between mb-16 md:mb-24 gap-8">
                    <div className="max-w-2xl">
                        <Badge 
                            variant="secondary" 
                            className="bg-accent/60 text-primary border border-primary/10 px-4 py-1.5 text-sm font-medium shadow-sm mb-6"
                        >
                            The Pipeline
                        </Badge>
                        <h2 className="text-3xl md:text-5xl font-bold text-charcoal tracking-tight mb-6 leading-tight">
                            How the extraction <br /> engine works
                        </h2>
                        <p className="text-lg text-charcoal/70 leading-relaxed">
                            A deterministic, three-stage pipeline that transforms your static PDF into a dynamic career asset in under 5 seconds.
                        </p>
                    </div>
                </div>

                <motion.div 
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-100px" }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 relative"
                >
                    <div className="hidden md:block absolute top-12 left-12 right-12 h-[1px] bg-border z-0" />

                    {steps.map((step, index) => (
                        <motion.div 
                            key={index} 
                            variants={itemVariants}
                            className="relative z-10 flex flex-col h-full bg-surface border border-border rounded-[2rem] p-8 md:p-10 shadow-sm hover:shadow-soft hover:-translate-y-1 transition-all duration-300"
                        >
                            <div className="flex items-center justify-between mb-12">
                                <div className="w-16 h-16 rounded-2xl bg-background border border-border flex items-center justify-center text-primary shadow-sm">
                                    {step.icon}
                                </div>
                                <span className="text-4xl font-black text-border/40 tracking-tighter">
                                    0{index + 1}
                                </span>
                            </div>
                            <h3 className="text-xl font-bold text-charcoal mb-4">
                                {step.title}
                            </h3>
                            <p className="text-charcoal/70 leading-relaxed">
                                {step.description}
                            </p>
                        </motion.div>
                    ))}
                </motion.div>

            </div>
        </section>
    );
}