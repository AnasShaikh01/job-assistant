type ProfileHeaderProps = {
    lastUpdated?: string;
};

export default function ProfileHeader({
    lastUpdated,
}: ProfileHeaderProps) {
    return (
        <section className="space-y-2">
            <h1 className="text-4xl font-bold">
                Candidate Profile
            </h1>

            <p className="text-gray-500">
                Manage your Candidate Knowledge Base
            </p>

            {lastUpdated && (
                <p className="text-sm text-gray-400">
                    Last updated:{" "}
                    {new Date(lastUpdated).toLocaleString()}
                </p>
            )}
        </section>
    );
}