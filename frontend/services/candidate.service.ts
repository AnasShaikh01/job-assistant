import { api } from "@/lib/api";
import {
    CandidateKnowledgeBase,
    CandidateProfile,
} from "@/types/candidate";

class CandidateService {
    async getProfile(
        token: string
    ): Promise<CandidateProfile> {
        const { data } = await api.get("/candidate/profile", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        return data.data;
    }

    async updateProfile(
        token: string,
        ckb: CandidateKnowledgeBase
    ): Promise<CandidateProfile> {
        const { data } = await api.patch(
            "/candidate/profile",
            { ckb },
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );

        return data.data;
    }
}

export const candidateService = new CandidateService();