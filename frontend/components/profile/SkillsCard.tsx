import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type SkillsCardProps = {
  profile: CandidateKnowledgeBase;
};

export default function SkillsCard({ profile }: SkillsCardProps) {
  return (
    <Card className="hover:shadow-lift transition-all duration-300">
      <CardHeader>
        <CardTitle className="text-2xl">Skills</CardTitle>
      </CardHeader>
      
      <CardContent>
        {profile.skills.length === 0 ? (
          <p className="text-muted-foreground text-sm">No skills found.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((skill, index) => (
              <Badge 
                key={index} 
                variant="secondary" 
                className="px-3 py-1.5 text-sm bg-accent text-primary hover:bg-accent/80 transition-colors"
              >
                {skill}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}