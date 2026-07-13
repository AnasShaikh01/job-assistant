import { CandidateKnowledgeBase } from "@/types/candidate";

type ProjectsSectionProps = {
    profile: CandidateKnowledgeBase;
};

export default function ProjectsSection({
    profile,
}: ProjectsSectionProps) {
    return (
        <section className="rounded-lg border p-6">
            <h2 className="mb-6 text-2xl font-semibold">
                Projects
            </h2>

            {profile.projects.length === 0 ? (
                <p className="text-gray-500">
                    No projects found.
                </p>
            ) : (
                <div className="space-y-6">
                    {profile.projects.map((project, index) => (
                        <div
                            key={index}
                            className="rounded-lg border p-5"
                        >
                            <h3 className="text-lg font-semibold">
                                {project.title}
                            </h3>

                            {project.description && (
                                <p className="mt-3 whitespace-pre-line text-gray-700">
                                    {project.description}
                                </p>
                            )}

                            <div className="mt-4 flex flex-wrap gap-4 text-sm">
                                {project.github && (
                                    <a
                                        href={project.github}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        GitHub
                                    </a>
                                )}

                                {project.live_url && (
                                    <a
                                        href={project.live_url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-blue-600 hover:underline"
                                    >
                                        Live Demo
                                    </a>
                                )}
                            </div>

                            {project.technologies.length > 0 && (
                                <div className="mt-4 flex flex-wrap gap-2">
                                    {project.technologies.map(
                                        (tech, techIndex) => (
                                            <span
                                                key={techIndex}
                                                className="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-700"
                                            >
                                                {tech}
                                            </span>
                                        )
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}