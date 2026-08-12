import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type ProjectsCardProps = {
    profile: CandidateKnowledgeBase;
};

export default function ProjectsCard({ profile }: ProjectsCardProps) {
    return (
        <Card className="hover:shadow-lift transition-all duration-300">
            <CardHeader>
                <CardTitle className="text-2xl">Projects</CardTitle>
            </CardHeader>

            <CardContent>
                {profile.projects.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No projects found.</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {profile.projects.map((project, index) => (
                            <div
                                key={index}
                                className="rounded-xl border border-border bg-background p-5 hover:border-primary/30 transition-colors flex flex-col h-full"
                            >
                                <h3 className="text-lg font-semibold text-charcoal mb-2">
                                    {project.title}
                                </h3>

                                {project.description && (
                                    <p className="text-sm text-charcoal/70 mb-4 flex-grow line-clamp-3">
                                        {project.description}
                                    </p>
                                )}

                                <div className="mt-auto space-y-4">
                                    {project.technologies.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5">
                                            {project.technologies.map((tech, techIndex) => (
                                                <Badge key={techIndex} variant="secondary" className="bg-accent/50 text-primary hover:bg-accent text-xs px-2 py-0.5">
                                                    {tech}
                                                </Badge>
                                            ))}
                                        </div>
                                    )}

                                    <div className="flex gap-4 text-sm font-medium pt-2 border-t border-border">
                                        {project.github && (
                                            <a href={project.github} target="_blank" rel="noreferrer" className="text-charcoal hover:text-primary transition-colors flex items-center gap-1">
                                                GitHub ↗
                                            </a>
                                        )}
                                        {project.live_url && (
                                            <a href={project.live_url} target="_blank" rel="noreferrer" className="text-charcoal hover:text-primary transition-colors flex items-center gap-1">
                                                Live Demo ↗
                                            </a>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}