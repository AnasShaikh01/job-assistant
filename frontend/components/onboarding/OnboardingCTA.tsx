"use client";

import { Button } from "@/components/ui/button";

export function OnboardingCTA() {
    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <section className="py-24 bg-background text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--color-accent)_0%,_transparent_50%)] opacity-30 pointer-events-none" />
            
            <div className="max-w-2xl mx-auto px-6 relative z-10">
                <h2 className="text-4xl font-bold text-charcoal mb-6 tracking-tight">
                    Ready to build your profile?
                </h2>
                <p className="text-lg text-charcoal/70 mb-10">
                    Join thousands of candidates who have stopped tweaking PDFs and started engineering their careers.
                </p>
                
                <Button 
                    onClick={scrollToTop}
                    size="lg" 
                    className="bg-primary text-white hover:bg-primary/90 shadow-soft hover:shadow-lift h-14 px-10 text-base rounded-xl transition-all"
                >
                    Upload Resume Now
                </Button>
            </div>
        </section>
    );
}