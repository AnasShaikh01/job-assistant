import { db } from "../../config/db";
import { resumeFiles } from "../../../drizzle/schema/resume-file.schema";

class ResumeRepository {
    async create(data: typeof resumeFiles.$inferInsert) {
        const [resume] = await db
            .insert(resumeFiles)
            .values(data)
            .returning();

        return resume;
    }
}

export const resumeRepository = new ResumeRepository();