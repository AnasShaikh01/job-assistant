import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type EducationCardProps = {
    profile: CandidateKnowledgeBase;
};

export default function EducationCard({ profile }: EducationCardProps) {
    return (
        <Card className="hover:shadow-lift transition-all duration-300">
            <CardHeader>
                <CardTitle className="text-2xl">Education</CardTitle>
            </CardHeader>

            <CardContent>
                {profile.education.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No education found.</p>
                ) : (
                    <div className="space-y-6">
                        {profile.education.map((education, index) => (
                            <div
                                key={index}
                                className="flex flex-col sm:flex-row justify-between items-start gap-4 pb-6 last:pb-0 border-b border-border last:border-0"
                            >
                                <div>
                                    <h3 className="text-lg font-semibold text-charcoal">
                                        {education.degree ?? "Degree Not Available"}
                                        {education.field_of_study && <span className="font-normal text-charcoal/70"> in {education.field_of_study}</span>}
                                    </h3>
                                    <p className="text-primary font-medium mt-1">
                                        {education.institution ?? "Institution Not Available"}
                                    </p>
                                    
                                    {education.cgpa && (
                                        <p className="mt-2 text-sm text-charcoal/80">
                                            <span className="font-medium text-charcoal">CGPA:</span> {education.cgpa}
                                        </p>
                                    )}
                                </div>
                                
                                <div className="text-sm font-medium text-charcoal/60 whitespace-nowrap">
                                    {education.start_year ?? "N/A"} - {education.end_year ?? "Present"}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}