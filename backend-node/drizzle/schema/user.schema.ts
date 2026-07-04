import {
    pgTable,
    uuid,
    varchar,
    boolean,
    timestamp,
    uniqueIndex,
} from "drizzle-orm/pg-core";

export const users = pgTable(
    "users",
    {
        id: uuid("id").defaultRandom().primaryKey(),

        clerkId: varchar("clerk_id", { length: 255 }).notNull(),

        email: varchar("email", { length: 255 }).notNull(),

        firstName: varchar("first_name", { length: 255 }),

        lastName: varchar("last_name", { length: 255 }),

        imageUrl: varchar("image_url", { length: 500 }),

        isOnboarded: boolean("is_onboarded").default(false).notNull(),

        createdAt: timestamp("created_at").defaultNow().notNull(),

        updatedAt: timestamp("updated_at")
            .defaultNow()
            .notNull(),
    },
    (table) => ({
        clerkIdIdx: uniqueIndex("users_clerk_id_idx").on(table.clerkId),

        emailIdx: uniqueIndex("users_email_idx").on(table.email),
    })
);