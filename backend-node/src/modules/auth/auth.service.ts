import { eq } from "drizzle-orm";
import { db } from "../../config/db";
import { users } from "../../../drizzle/schema/user.schema";

type ClerkUserData = {
    clerkId: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
    imageUrl: string | null;
};

class AuthService {
    async syncUser(userData: ClerkUserData) {
        // Check if user already exists
        const [existingUser] = await db
            .select()
            .from(users)
            .where(eq(users.clerkId, userData.clerkId));

        if (existingUser) {
            return existingUser;
        }

        // Create new user
        const [newUser] = await db
            .insert(users)
            .values({
                clerkId: userData.clerkId,
                email: userData.email,
                firstName: userData.firstName,
                lastName: userData.lastName,
                imageUrl: userData.imageUrl,
            })
            .returning();

        return newUser;
    }
}

export const authService = new AuthService();