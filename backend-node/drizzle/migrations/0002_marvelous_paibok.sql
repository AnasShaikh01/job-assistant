ALTER TYPE "public"."resume_status" RENAME TO "processing_status";--> statement-breakpoint
ALTER TABLE "resume_files" RENAME COLUMN "storage_path" TO "storage_key";--> statement-breakpoint
ALTER TABLE "resume_files" RENAME COLUMN "status" TO "processing_status";