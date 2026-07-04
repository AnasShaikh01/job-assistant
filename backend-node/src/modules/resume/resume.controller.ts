import { Request, Response } from "express";
import { getAuth } from "@clerk/express";

import { authService } from "../auth/auth.service";
import { resumeService } from "./resume.service";

export const uploadResume = async (
    req: Request,
    res: Response
) => {
    try {
        const { userId: clerkUserId } = getAuth(req);

        if (!clerkUserId) {
            return res.status(401).json({
                success: false,
                message: "Unauthorized",
            });
        }

        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: "No resume uploaded.",
            });
        }

        // Find application user
        const dbUser = await authService.findByClerkId(clerkUserId);

        if (!dbUser) {
            return res.status(404).json({
                success: false,
                message: "User not found.",
            });
        }

        // Upload + Save metadata
        const resume = await resumeService.uploadResume(
            req.file,
            dbUser
        );

        return res.status(201).json({
            success: true,
            message: "Resume uploaded successfully.",
            data: resume,
        });
    } catch (error) {
        console.error(error);

        return res.status(500).json({
            success: false,
            message: "Failed to upload resume.",
        });
    }
};