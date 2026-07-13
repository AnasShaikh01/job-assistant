import { CandidateKnowledgeBase } from "@/types/candidate";

type ExperienceSectionProps = {
    profile: CandidateKnowledgeBase;
};

export default function ExperienceSection({
    profile,
}: ExperienceSectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-6 text-2xl font-semibold">
                Experience
            </h2>

            {profile.experience.length === 0 ? (
                <p className="text-gray-500">
                    No experience found.
                </p>
            ) : (
                <div className="space-y-6">
                    {profile.experience.map(
                        (experience, index) => (
                            <div
                                key={index}
                                className="rounded-lg border p-5"
                            >
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h3 className="text-lg font-semibold">
                                            {experience.role ||
                                                "Role Not Available"}
                                        </h3>

                                        <p className="text-gray-600">
                                            {experience.company ||
                                                "Company Not Available"}
                                        </p>
                                    </div>

                                    <div className="text-right text-sm text-gray-500">
                                        {(experience.start_date ||
                                            "N/A") +
                                            " - " +
                                            (experience.end_date ||
                                                "Present")}
                                    </div>
                                </div>

                                {experience.description && (
                                    <p className="mt-4 whitespace-pre-line text-gray-700">
                                        {
                                            experience.description
                                        }
                                    </p>
                                )}

                                {experience.technologies
                                    .length > 0 && (
                                        <div className="mt-4 flex flex-wrap gap-2">
                                            {experience.technologies.map(
                                                (
                                                    tech,
                                                    techIndex
                                                ) => (
                                                    <span
                                                        key={
                                                            techIndex
                                                        }
                                                        className="rounded-full bg-green-100 px-3 py-1 text-sm text-green-700"
                                                    >
                                                        {tech}
                                                    </span>
                                                )
                                            )}
                                        </div>
                                    )}
                            </div>
                        )
                    )}
                </div>
            )}
        </section>
    );
}