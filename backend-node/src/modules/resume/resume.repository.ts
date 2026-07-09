import { eq } from "drizzle-orm";
import { db } from "../../config/db";
import { resumeFiles } from "../../../drizzle/schema/resume-file.schema";

class ResumeRepository {
    async create(data: typeof resumeFiles.$inferInsert) {
        const [resume] = await db.insert(resumeFiles).values(data).returning();
        return resume;
    }

    async updateProcessingStatus(
        id: string, 
        status: "UPLOADED" | "PROCESSING" | "COMPLETED" | "FAILED"
    ) {
        const [updatedResume] = await db
            .update(resumeFiles)
            .set({
                processingStatus: status,
                updatedAt: new Date(),
            })
            .where(eq(resumeFiles.id, id))
            .returning();

        return updatedResume;
    }
}

export const resumeRepository = new ResumeRepository();