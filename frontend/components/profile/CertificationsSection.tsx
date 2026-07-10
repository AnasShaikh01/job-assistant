import { CandidateKnowledgeBase } from "@/types/candidate";

type CertificationsSectionProps = {
    profile: CandidateKnowledgeBase;
};

export default function CertificationsSection({
    profile,
}: CertificationsSectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-6 text-2xl font-semibold">
                Certifications
            </h2>

            {profile.certifications.length === 0 ? (
                <p className="text-gray-500">
                    No certifications found.
                </p>
            ) : (
                <div className="space-y-4">
                    {profile.certifications.map(
                        (certification, index) => (
                            <div
                                key={index}
                                className="rounded-lg border p-5"
                            >
                                <h3 className="text-lg font-semibold">
                                    {certification.name ??
                                        "Certification"}
                                </h3>

                                {certification.issuer && (
                                    <p className="mt-1 text-gray-600">
                                        {certification.issuer}
                                    </p>
                                )}

                                <div className="mt-3 flex flex-wrap gap-6 text-sm text-gray-500">
                                    {certification.issue_date && (
                                        <span>
                                            <strong>
                                                Issued:
                                            </strong>{" "}
                                            {
                                                certification.issue_date
                                            }
                                        </span>
                                    )}

                                    {certification.expiry_date && (
                                        <span>
                                            <strong>
                                                Expires:
                                            </strong>{" "}
                                            {
                                                certification.expiry_date
                                            }
                                        </span>
                                    )}

                                    {certification.credential_id && (
                                        <span>
                                            <strong>ID:</strong>{" "}
                                            {
                                                certification.credential_id
                                            }
                                        </span>
                                    )}
                                </div>

                                {certification.credential_url && (
                                    <a
                                        href={
                                            certification.credential_url
                                        }
                                        target="_blank"
                                        rel="noreferrer"
                                        className="mt-3 inline-block text-blue-600 hover:underline"
                                    >
                                        View Credential
                                    </a>
                                )}
                            </div>
                        )
                    )}
                </div>
            )}
        </section>
    );
}