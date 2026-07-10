import { CandidateKnowledgeBase } from "@/types/candidate";

type EducationSectionProps = {
    profile: CandidateKnowledgeBase;
};

export default function EducationSection({
    profile,
}: EducationSectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-6 text-2xl font-semibold">
                Education
            </h2>

            {profile.education.length === 0 ? (
                <p className="text-gray-500">
                    No education found.
                </p>
            ) : (
                <div className="space-y-6">
                    {profile.education.map(
                        (education, index) => (
                            <div
                                key={index}
                                className="rounded-lg border p-5"
                            >
                                <h3 className="text-lg font-semibold">
                                    {education.degree ??
                                        "Degree Not Available"}
                                </h3>

                                <p className="mt-1 text-gray-600">
                                    {education.institution ??
                                        "Institution Not Available"}
                                </p>

                                {education.field_of_study && (
                                    <p className="mt-2 text-gray-700">
                                        <span className="font-medium">
                                            Field:
                                        </span>{" "}
                                        {
                                            education.field_of_study
                                        }
                                    </p>
                                )}

                                <div className="mt-3 flex flex-wrap gap-6 text-sm text-gray-500">
                                    <span>
                                        <strong>Start:</strong>{" "}
                                        {education.start_year ??
                                            "N/A"}
                                    </span>

                                    <span>
                                        <strong>End:</strong>{" "}
                                        {education.end_year ??
                                            "Present"}
                                    </span>

                                    {education.cgpa && (
                                        <span>
                                            <strong>CGPA:</strong>{" "}
                                            {education.cgpa}
                                        </span>
                                    )}
                                </div>
                            </div>
                        )
                    )}
                </div>
            )}
        </section>
    );
}