import { eq } from "drizzle-orm";
import { db } from "../../config/db";
import { candidateProfiles } from "../../../drizzle/schema/candidate-profile.schema";

class CandidateRepository {
    /**
     * Create a candidate profile after resume parsing.
     */
    async saveCandidateProfile(data: {
        userId: string;
        resumeFileId: string;
        ckb: any;
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

    /**
     * Get candidate profile by user ID.
     */
    async findByUserId(userId: string) {
        const [candidateProfile] = await db
            .select()
            .from(candidateProfiles)
            .where(eq(candidateProfiles.userId, userId));

        return candidateProfile ?? null;
    }

    /**
     * Update only the CKB.
     */
    async updateCKB(userId: string, ckb: any) {
        const [updatedProfile] = await db
            .update(candidateProfiles)
            .set({
                ckb,
                // Remove this line if your schema doesn't have updatedAt
                updatedAt: new Date(),
            })
            .where(eq(candidateProfiles.userId, userId))
            .returning();

        return updatedProfile ?? null;
    }

    /**
 * Update candidate profile after uploading a new resume.
 * Updates both the linked resume and the parsed CKB.
 */
    async updateCandidateProfile(data: {
        userId: string;
        resumeFileId: string;
        ckb: any;
    }) {
        const [updatedProfile] = await db
            .update(candidateProfiles)
            .set({
                resumeFileId: data.resumeFileId,
                ckb: data.ckb,
                updatedAt: new Date(),
            })
            .where(eq(candidateProfiles.userId, data.userId))
            .returning();

        return updatedProfile ?? null;
    }
}

export const candidateRepository = new CandidateRepository();