import { Badge } from "@/components/ui/badge";
import { CheckCircle2, ScanSearch, LineChart, FileEdit } from "lucide-react";

export function OnboardingFeatures() {
    const features = [
        {
            icon: <ScanSearch className="w-6 h-6" />,
            title: "ATS Keyword Mapping",
            description: "We identify exactly which technical skills and tools are present in your resume, ensuring they aren't hidden inside dense paragraphs."
        },
        {
            icon: <LineChart className="w-6 h-6" />,
            title: "Impact Metric Extraction",
            description: "Our AI scans for percentages, revenue figures, and team sizes—the exact metrics recruiters look for to prove your competency."
        },
        {
            icon: <CheckCircle2 className="w-6 h-6" />,
            title: "Format Normalization",
            description: "No matter how chaotic your PDF layout is, our system strips away the noise and structures your history perfectly."
        },
        {
            icon: <FileEdit className="w-6 h-6" />,
            title: "Interactive Editing",
            description: "Once parsed, you enter a notion-style editor where you can tweak, expand, and refine your Knowledge Base before applying."
        }
    ];

    return (
        <section className="py-24 bg-background">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex flex-col lg:flex-row gap-16 items-center">
                    
                    {/* Left side text */}
                    <div className="w-full lg:w-5/12 space-y-6">
                        <Badge variant="secondary" className="bg-accent/60 text-primary border border-primary/10 px-4 py-1.5">
                            Deep Analysis
                        </Badge>
                        <h2 className="text-3xl md:text-5xl font-bold text-charcoal leading-tight tracking-tight">
                            Beyond standard <br/> PDF parsing.
                        </h2>
                        <p className="text-lg text-charcoal/70 leading-relaxed">
                            Traditional parsers fail when they encounter multi-column layouts or complex formatting. PrimeVex uses vision-capable AI to understand your document exactly how a human recruiter would.
                        </p>
                    </div>

                    {/* Right side Grid */}
                    <div className="w-full lg:w-7/12 grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {features.map((feature, index) => (
                            <div 
                                key={index} 
                                className="bg-surface border border-border p-8 rounded-2xl shadow-sm hover:shadow-soft transition-all duration-300"
                            >
                                <div className="w-12 h-12 rounded-xl bg-accent/40 text-primary flex items-center justify-center mb-6">
                                    {feature.icon}
                                </div>
                                <h3 className="text-lg font-bold text-charcoal mb-2">{feature.title}</h3>
                                <p className="text-sm text-charcoal/70 leading-relaxed">{feature.description}</p>
                            </div>
                        ))}
                    </div>

                </div>
            </div>
        </section>
    );
}