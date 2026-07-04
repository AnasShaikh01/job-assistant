import { randomUUID } from "crypto";
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "../config/s3";

class StorageService {
    async uploadResume(file: Express.Multer.File, userId: string) {
        const extension = file.originalname.split(".").pop();

        const storageKey = `users/${userId}/${randomUUID()}.${extension}`;

        await s3Client.send(
            new PutObjectCommand({
                Bucket: process.env.SUPABASE_S3_BUCKET!,
                Key: storageKey,
                Body: file.buffer,
                ContentType: file.mimetype,
            })
        );

        return {
            storageKey,
        };
    }
}

export const storageService = new StorageService();