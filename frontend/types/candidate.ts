export interface CandidateLinks {
    github: string | null;
    linkedin: string | null;
    portfolio: string | null;
    other: string[];
}

export interface CandidateExperience {
    company: string | null;
    role: string;
    start_date: string | null;
    end_date: string | null;
    description: string;
    technologies: string[];
}

export interface CandidateEducation {
    institution: string | null;
    degree: string;
    field_of_study: string | null;
    start_year: string | null;
    end_year: string | null;
    cgpa: string | null;
}

export interface CandidateProject {
    title: string;
    description: string;
    github: string | null;
    live_url: string | null;
    technologies: string[];
}

export interface CandidateCertification {
    name?: string;
    issuer?: string;
    issue_date?: string;
    expiry_date?: string;
    credential_id?: string;
    credential_url?: string;
}

export interface CandidateKnowledgeBase {
    summary: string;

    skills: string[];

    experience: CandidateExperience[];

    education: CandidateEducation[];

    projects: CandidateProject[];

    certifications: CandidateCertification[];

    links: CandidateLinks;
}

export interface CandidateProfile {
    id: string;
    userId: string;
    resumeFileId: string;

    ckb: CandidateKnowledgeBase;

    createdAt: string;
    updatedAt: string;
}