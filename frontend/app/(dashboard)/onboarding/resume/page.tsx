import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { OnboardingHero } from "@/components/onboarding/OnboardingHero";
import { OnboardingLogos } from "@/components/onboarding/OnboardingLogoCloud";
import { OnboardingHowItWorks } from "@/components/onboarding/OnboardingHowItWorks";
import { OnboardingFeatures } from "@/components/onboarding/OnboardingFeatures";
import { OnboardingFAQ } from "@/components/onboarding/OnboardingFAQ";
import { OnboardingCTA } from "@/components/onboarding/OnboardingCTA";

export default function ResumeOnboardingPage() {
    return (
        <main className="min-h-screen w-full bg-background flex flex-col relative overflow-hidden">
            {/* Top Glow matching landing page */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[600px] bg-[radial-gradient(ellipse_at_top,_var(--color-accent),_transparent_70%)] opacity-50 pointer-events-none" />
            
            <Navbar />
            
            <div className="flex-1 relative z-10 w-full">
                {/* 1. Hero & Tool */}
                <OnboardingHero />
                
                {/* 2. Trusted By Logos */}
                <OnboardingLogos />
                
                {/* 3. The 3-Step Process */}
                <OnboardingHowItWorks />
                
                {/* 4. Deep Dive Features */}
                <OnboardingFeatures />
                
                {/* 5. Frequently Asked Questions */}
                <OnboardingFAQ />
                
                {/* 6. Final Call to Action */}
                <OnboardingCTA />
            </div>

            <Footer />
        </main>
    );
}