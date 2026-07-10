import { candidateRepository } from "./candidate.repository";

class CandidateService {
    async getProfile(userId: string) {
        const profile = await candidateRepository.findByUserId(userId);

        if (!profile) {
            throw new Error("Candidate profile not found");
        }

        return profile;
    }

    async updateProfile(userId: string, ckb: any) {
        // Check ownership / existence
        const profile = await candidateRepository.findByUserId(userId);

        if (!profile) {
            throw new Error("Candidate profile not found");
        }

        const updatedProfile = await candidateRepository.updateCKB(userId, ckb);

        return updatedProfile;
    }
}

export const candidateService = new CandidateService();