import { randomUUID } from "crypto";
import { storageService } from "../../services/storage.service";
import { pythonService } from "../../services/python.service";
import { resumeRepository } from "./resume.repository";
import { candidateRepository } from "../candidate/candidate.repository";

class ResumeService {
    async uploadResume(
        file: Express.Multer.File,
        user: { id: string }
    ) {
        const resumeId = randomUUID();

        // Upload to Storage
        const { storageKey } = await storageService.uploadResume(file, user.id, resumeId);

        let resume;
        try {
            // Save metadata in Neon (Initial state: UPLOADED)
            resume = await resumeRepository.create({
                id: resumeId,
                userId: user.id,
                originalName: file.originalname,
                storedName: storageKey.split("/").pop()!,
                storageKey,
                mimeType: file.mimetype,
                size: file.size,
                processingStatus: "UPLOADED",
            });
        } catch (dbError: any) {
            // ROLLBACK: Delete the S3 object if database insertion fails
            await storageService.deleteResume(storageKey).catch(err =>
                console.error(`[Rollback Failed] Could not delete ${storageKey}:`, err)
            );
            throw new Error(`Failed to save resume metadata: ${dbError.message}`);
        }

        try {
            // Update status to PROCESSING before sending to Python
            await resumeRepository.updateProcessingStatus(resume.id, "PROCESSING");

            // Generate URL & Call Python
            const fileUrl = await storageService.createSignedUrl(
                process.env.SUPABASE_RESUME_BUCKET!,
                storageKey
            ); const pythonResponse = await pythonService.parseResume(
                resume.id,
                fileUrl,
                file.originalname
            );

            // 2. Save or update the Candidate Knowledge Base (CKB)

            const existingProfile = await candidateRepository.findByUserId(
                user.id
            );

            if (existingProfile) {
                await candidateRepository.updateCandidateProfile({
                    userId: user.id,
                    resumeFileId: resume.id,
                    ckb: pythonResponse.candidate,
                });
            } else {
                await candidateRepository.saveCandidateProfile({
                    userId: user.id,
                    resumeFileId: resume.id,
                    ckb: pythonResponse.candidate,
                });
            }

            // 3. Mark the resume processing lifecycle as COMPLETED
            await resumeRepository.updateProcessingStatus(resume.id, "COMPLETED");

            return {
                message: "Resume uploaded and processing successfully completed.",
                resumeMetadata: {
                    id: resume.id,
                    status: "COMPLETED"
                }
            };

        } catch (error: any) {
            // Handle failures gracefully in DB, then throw to the Controller
            await resumeRepository.updateProcessingStatus(resume.id, "FAILED");

            const errorMessage = error?.response?.data?.detail || error.message;
            console.error(`[ResumeService] Parsing failed for ${resume.id}:`, errorMessage);

            throw new Error(`Resume parsing failed: ${errorMessage}`);
        }
    }
}

export const resumeService = new ResumeService();