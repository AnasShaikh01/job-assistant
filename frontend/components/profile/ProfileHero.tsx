import { Card, CardContent } from "@/components/ui/card";

type ProfileHeroProps = {
    lastUpdated?: string;
};

export default function ProfileHero({ lastUpdated }: ProfileHeroProps) {
    return (
        <Card className="bg-gradient-to-br from-surface to-accent/20 border-border/50">
            <CardContent className="pt-8 pb-8">
                <h1 className="text-3xl md:text-4xl font-bold text-charcoal tracking-tight mb-2">
                    Candidate Knowledge Base
                </h1>
                <p className="text-base text-charcoal/70 mb-4 max-w-2xl">
                    This is your central career brain. The AI uses this data to match you with jobs, generate tailored resumes, and auto-draft cover letters.
                </p>
                {lastUpdated && (
                    <div className="inline-flex items-center rounded-full bg-surface px-3 py-1 text-xs font-medium text-charcoal/60 border border-border shadow-sm">
                        <span className="w-2 h-2 rounded-full bg-success mr-2"></span>
                        Last updated: {new Date(lastUpdated).toLocaleString(undefined, { 
                            dateStyle: 'medium', 
                            timeStyle: 'short' 
                        })}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}