import { db } from "../../config/db";
import { candidateProfiles } from "../../../drizzle/schema/candidate-profile.schema"; 

class CandidateRepository {
    async saveCandidateProfile(data: {
        userId: string;
        resumeFileId: string;
        ckb: any; // The structured JSON from Python
    }) {
        const [candidateProfile] = await db
            .insert(candidateProfiles)
            .values({
                userId: data.userId,
                resumeFileId: data.resumeFileId,
                ckb: data.ckb, 
            })
            .returning();

        return candidateProfile;
    }
}

export const candidateRepository = new CandidateRepository();