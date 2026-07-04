import {
    pgTable,
    uuid,
    varchar,
    integer,
    timestamp,
    pgEnum,
} from "drizzle-orm/pg-core";

import { users } from "./user.schema";

export const processingStatusEnum = pgEnum("processing_status", [
    "UPLOADED",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
]);

export const resumeFiles = pgTable("resume_files", {
    id: uuid("id").defaultRandom().primaryKey(),

    userId: uuid("user_id")
        .notNull()
        .references(() => users.id, {
            onDelete: "cascade",
        }),

    originalName: varchar("original_name", { length: 255 }).notNull(),

    storedName: varchar("stored_name", { length: 255 }).notNull(),

    storageKey: varchar("storage_key", { length: 500 }).notNull(),

    mimeType: varchar("mime_type", { length: 100 }).notNull(),

    size: integer("size").notNull(),

    processingStatus: processingStatusEnum("processing_status")
        .default("UPLOADED")
        .notNull(),

    createdAt: timestamp("created_at").defaultNow().notNull(),

    updatedAt: timestamp("updated_at")
        .defaultNow()
        .notNull(),
});