import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type CertificationsCardProps = {
    profile: CandidateKnowledgeBase;
};

export default function CertificationsCard({ profile }: CertificationsCardProps) {
    return (
        <Card className="hover:shadow-lift transition-all duration-300">
            <CardHeader>
                <CardTitle className="text-2xl">Certifications</CardTitle>
            </CardHeader>

            <CardContent>
                {profile.certifications.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No certifications found.</p>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {profile.certifications.map((certification, index) => (
                            <div
                                key={index}
                                className="rounded-xl border border-border bg-background p-5 hover:border-primary/30 transition-colors"
                            >
                                <h3 className="text-base font-semibold text-charcoal">
                                    {certification.name ?? "Certification"}
                                </h3>

                                {certification.issuer && (
                                    <p className="mt-1 text-sm text-primary font-medium">
                                        {certification.issuer}
                                    </p>
                                )}

                                <div className="mt-3 flex flex-wrap gap-2">
                                    {certification.issue_date && (
                                        <Badge variant="outline" className="text-xs text-charcoal/60">
                                            Issued: {certification.issue_date}
                                        </Badge>
                                    )}
                                    {certification.expiry_date && (
                                        <Badge variant="outline" className="text-xs text-charcoal/60">
                                            Expires: {certification.expiry_date}
                                        </Badge>
                                    )}
                                </div>

                                {(certification.credential_id || certification.credential_url) && (
                                    <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-sm">
                                        {certification.credential_id ? (
                                            <span className="text-charcoal/50 font-mono text-xs truncate mr-2">
                                                ID: {certification.credential_id}
                                            </span>
                                        ) : <div />}
                                        
                                        {certification.credential_url && (
                                            <a
                                                href={certification.credential_url}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="text-primary hover:underline whitespace-nowrap font-medium"
                                            >
                                                View ↗
                                            </a>
                                        )}
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