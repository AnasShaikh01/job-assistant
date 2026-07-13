import { CandidateKnowledgeBase } from "@/types/candidate";

type SkillsSectionProps = {
    profile: CandidateKnowledgeBase;
};

export default function SkillsSection({
    profile,
}: SkillsSectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-4 text-2xl font-semibold">
                Skills
            </h2>

            {profile.skills.length === 0 ? (
                <p className="text-gray-500">
                    No skills found.
                </p>
            ) : (
                <div className="flex flex-wrap gap-3">
                    {profile.skills.map((skill, index) => (
                        <span
                            key={index}
                            className="rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700"
                        >
                            {skill}
                        </span>
                    ))}
                </div>
            )}
        </section>
    );
}