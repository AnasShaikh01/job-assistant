import {
    pgTable,
    uuid,
    jsonb,
    timestamp,
} from "drizzle-orm/pg-core";

import { users } from "./user.schema";
import { resumeFiles } from "./resume-file.schema";

export const candidateProfiles = pgTable("candidate_profiles", {
    id: uuid("id").defaultRandom().primaryKey(),

    userId: uuid("user_id")
        .notNull()
        .references(() => users.id, {
            onDelete: "cascade",
        }),

    resumeFileId: uuid("resume_file_id")
        .notNull()
        .references(() => resumeFiles.id, {
            onDelete: "cascade",
        }),

    ckb: jsonb("ckb").notNull(),

    createdAt: timestamp("created_at")
        .defaultNow()
        .notNull(),

    updatedAt: timestamp("updated_at")
        .defaultNow()
        .notNull(),
});