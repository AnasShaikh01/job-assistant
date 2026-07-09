import { PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { s3Client } from "../config/s3";

class StorageService {
    async uploadResume(file: Express.Multer.File, userId: string, resumeId: string) {
        const extension = file.originalname.split(".").pop();
        const storageKey = `users/${userId}/${resumeId}.${extension}`;

        await s3Client.send(
            new PutObjectCommand({
                Bucket: process.env.SUPABASE_S3_BUCKET!,
                Key: storageKey,
                Body: file.buffer,
                ContentType: file.mimetype,
            })
        );

        return { storageKey };
    }

    async createSignedUrl(storageKey: string, expiresInSeconds: number = 3600) {
        const command = new GetObjectCommand({
            Bucket: process.env.SUPABASE_S3_BUCKET!,
            Key: storageKey,
        });

        return await getSignedUrl(s3Client, command, { expiresIn: expiresInSeconds });
    }

    // NEW: Rollback method to delete the orphan file
    async deleteResume(storageKey: string) {
        await s3Client.send(
            new DeleteObjectCommand({
                Bucket: process.env.SUPABASE_S3_BUCKET!,
                Key: storageKey,
            })
        );
    }
}

export const storageService = new StorageService();