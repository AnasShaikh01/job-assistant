import { CandidateKnowledgeBase } from "@/types/candidate";

type SummarySectionProps = {
    profile: CandidateKnowledgeBase;
    setProfile: React.Dispatch<
        React.SetStateAction<CandidateKnowledgeBase>
    >;
};

export default function SummarySection({
    profile,
    setProfile,
}: SummarySectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-4 text-2xl font-semibold">
                Professional Summary
            </h2>

            <textarea
                rows={8}
                className="w-full rounded-md border p-3"
                value={profile.summary}
                placeholder="Write your professional summary..."
                onChange={(e) =>
                    setProfile((prev) => ({
                        ...prev,
                        summary: e.target.value,
                    }))
                }
            />
        </section>
    );
}