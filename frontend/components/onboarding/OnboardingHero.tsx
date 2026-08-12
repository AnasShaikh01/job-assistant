import { Badge } from "@/components/ui/badge";
import { OnboardingSidebar } from "./OnboardingSidebar";
import { UploadWorkspace } from "./UploadWorkspace";

export function OnboardingHero() {
    return (
        <section className="relative w-full max-w-7xl mx-auto px-6 pt-24 md:pt-28 pb-16">
            <div className="text-center max-w-3xl mx-auto mb-16 space-y-6">
                <Badge 
                    variant="secondary" 
                    className="bg-accent/60 text-primary border border-primary/10 px-4 py-1.5 text-sm font-medium shadow-sm"
                >
                    Step 1: Data Ingestion
                </Badge>
                
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-charcoal tracking-tight leading-[1.1]">
                    Initialize your <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-hover">
                        Candidate Knowledge Base
                    </span>
                </h1>
                
                <p className="text-lg md:text-xl text-charcoal/70 max-w-2xl mx-auto leading-relaxed">
                    Upload your latest resume. Our engine will instantly extract your professional history, map your technical skills, and structure your data.
                </p>
            </div>

            <div className="relative max-w-6xl mx-auto">
                <div className="absolute -inset-2 bg-gradient-to-tr from-accent to-surface blur-2xl opacity-60 rounded-[3rem] -z-10" />
                
                <div className="w-full rounded-[2.5rem] border border-border bg-surface shadow-soft hover:shadow-lift transition-all duration-500 overflow-hidden flex flex-col lg:flex-row relative z-10">
                    <div className="w-full lg:w-[420px] shrink-0 border-b lg:border-b-0 lg:border-r border-border bg-background/80 backdrop-blur-md">
                        <OnboardingSidebar />
                    </div>

                    <div className="flex-1 p-8 md:p-12 lg:p-16 flex flex-col justify-center relative bg-surface">
                        <div className="absolute inset-0 bg-gradient-to-br from-background/40 to-transparent pointer-events-none" />
                        
                        <div className="relative z-10 w-full max-w-xl mx-auto">
                            <UploadWorkspace />
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}