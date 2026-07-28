import { randomUUID } from "crypto";

import { storageService } from "../../services/storage.service";
import { pythonService } from "../../services/python.service";

class JobsService {
    async uploadJobDescription(
        file: Express.Multer.File,
        user: { id: string }
    ) {
        const jobFileId = randomUUID();
        console.log("Uploading JD...");

        // Upload JD to Supabase Storage
        const { storageKey } =
            await storageService.uploadJobDescription(
                file,
                user.id,
                jobFileId
            );

        console.log("Storage key:", storageKey);

        // Generate signed URL
        const fileUrl = await storageService.createSignedUrl(
            process.env.SUPABASE_JOB_BUCKET!,
            storageKey
        );

        console.log("Signed URL:", fileUrl);

        // Parse JD
        try {
            const pythonResponse = await pythonService.parseJob(
                jobFileId,
                fileUrl,
                file.originalname
            );

            console.log("Python response received");

            return pythonResponse;
        } catch (err) {
            console.error("Python parse failed:", err);
            throw err;
        }
    }

    async parseJobFromUrl(url: string) {
        try {
            const pythonResponse = await pythonService.parseJobFromUrl(url);

            return pythonResponse;
        } catch (err) {
            console.error("Python parse failed:", err);
            throw err;
        }
    }

    async parseJobFromText(text: string) {
        try {
            const pythonResponse = await pythonService.parseJobFromText(text);

            return pythonResponse;
        } catch (err) {
            console.error("Python parse failed:", err);
            throw err;
        }
    }
}

export const jobsService = new JobsService();