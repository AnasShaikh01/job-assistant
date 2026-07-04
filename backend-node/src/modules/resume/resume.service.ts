import { storageService } from "../../services/storage.service";
import { resumeRepository } from "./resume.repository";

class ResumeService {
    async uploadResume(
        file: Express.Multer.File,
        user: {
            id: string;
        }
    ) {
        // Upload file to Supabase Storage
        const { storageKey } = await storageService.uploadResume(
            file,
            user.id
        );

        // Save metadata in Neon
        const resume = await resumeRepository.create({
            userId: user.id,

            originalName: file.originalname,

            storedName: storageKey.split("/").pop()!,

            storageKey,

            mimeType: file.mimetype,

            size: file.size,
        });

        return resume;
    }
}

export const resumeService = new ResumeService();