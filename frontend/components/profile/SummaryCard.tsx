import { CandidateKnowledgeBase } from "@/types/candidate";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type SummaryCardProps = {
  profile: CandidateKnowledgeBase;
  setProfile: React.Dispatch<React.SetStateAction<CandidateKnowledgeBase>>;
};

export default function SummaryCard({ profile, setProfile }: SummaryCardProps) {
  return (
    <Card className="hover:shadow-lift transition-all duration-300">
      <CardHeader>
        <CardTitle className="text-2xl">Professional Summary</CardTitle>
      </CardHeader>
      
      <CardContent>
        <textarea
          rows={6}
          className="w-full rounded-xl border border-border bg-background p-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all resize-y"
          value={profile.summary}
          placeholder="Write a brief professional summary focusing on your key achievements..."
          onChange={(e) =>
            setProfile((prev) => ({
              ...prev,
              summary: e.target.value,
            }))
          }
        />
      </CardContent>
    </Card>
  );
}