import { Request, Response } from "express";
import { getAuth, clerkClient } from "@clerk/express";
import { authService } from "./auth.service";

export const getCurrentUser = async (
    req: Request,
    res: Response
) => {
    try {
        const { userId } = getAuth(req);

        if (!userId) {
            return res.status(401).json({
                success: false,
                message: "Unauthorized",
            });
        }

        const user = await clerkClient.users.getUser(userId);

        const dbUser = await authService.syncUser({
            clerkId: user.id,
            email: user.emailAddresses[0]?.emailAddress ?? "",
            firstName: user.firstName,
            lastName: user.lastName,
            imageUrl: user.imageUrl,
        });

        return res.status(200).json({
            success: true,
            user: dbUser,
        });
    } catch (error) {
        console.error(error);

        return res.status(500).json({
            success: false,
            message: "Internal Server Error",
        });
    }
};