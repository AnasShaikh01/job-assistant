import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type ExperienceCardProps = {
    profile: CandidateKnowledgeBase;
};

export default function ExperienceCard({ profile }: ExperienceCardProps) {
    return (
        <Card className="hover:shadow-lift transition-all duration-300">
            <CardHeader>
                <CardTitle className="text-2xl">Experience</CardTitle>
            </CardHeader>

            <CardContent>
                {profile.experience.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No experience found.</p>
                ) : (
                    <div className="space-y-6">
                        {profile.experience.map((experience, index) => (
                            <div
                                key={index}
                                className="group relative pl-4 border-l-2 border-border hover:border-primary transition-colors pb-6 last:pb-0"
                            >
                                <div className="absolute w-3 h-3 bg-surface border-2 border-border group-hover:border-primary rounded-full -left-[7px] top-1.5 transition-colors"></div>
                                
                                <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-2 gap-2">
                                    <div>
                                        <h3 className="text-lg font-semibold text-charcoal">
                                            {experience.role || "Role Not Available"}
                                        </h3>
                                        <p className="text-primary font-medium text-sm">
                                            {experience.company || "Company Not Available"}
                                        </p>
                                    </div>
                                    <div className="text-sm font-medium text-charcoal/60 bg-accent/50 px-3 py-1 rounded-md h-fit whitespace-nowrap">
                                        {(experience.start_date || "N/A") + " - " + (experience.end_date || "Present")}
                                    </div>
                                </div>

                                {experience.description && (
                                    <p className="mt-3 whitespace-pre-line text-sm text-charcoal/80 leading-relaxed">
                                        {experience.description}
                                    </p>
                                )}

                                {experience.technologies.length > 0 && (
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        {experience.technologies.map((tech, techIndex) => (
                                            <Badge key={techIndex} variant="outline" className="bg-surface">
                                                {tech}
                                            </Badge>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}