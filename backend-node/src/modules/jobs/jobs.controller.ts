import { Request, Response } from "express";
import { getAuth } from "@clerk/express";

import { authService } from "../auth/auth.service";
import { jobsService } from "./jobs.service";

export const uploadJobDescription = async (
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
                message: "No job description uploaded.",
            });
        }

        const dbUser = await authService.findByClerkId(clerkUserId);

        if (!dbUser) {
            return res.status(404).json({
                success: false,
                message: "User not found.",
            });
        }

        const result = await jobsService.uploadJobDescription(
            req.file,
            dbUser
        );

        return res.status(201).json({
            success: true,
            message: "Job description uploaded successfully.",
            data: result,
        });
    } catch (error) {
        console.error(error);

        return res.status(500).json({
            success: false,
            message: "Failed to upload job description.",
        });
    }
};

export const parseJobFromUrl = async (
    req: Request,
    res: Response
) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({
                success: false,
                message: "Job URL is required.",
            });
        }

        const result = await jobsService.parseJobFromUrl(url);

        return res.status(200).json({
            success: true,
            message: "Job parsed successfully.",
            data: result,
        });
    } catch (error: any) {
        console.error(error);

        return res.status(
            error?.response?.status || 500
        ).json({
            success: false,
            message:
                error?.response?.data?.detail ||
                "Failed to parse job URL.",
        });
    }
};

export const parseJobFromText = async (
    req: Request,
    res: Response
) => {
    try {
        const { text } = req.body;

        if (!text) {
            return res.status(400).json({
                success: false,
                message: "Job description text is required.",
            });
        }

        const result = await jobsService.parseJobFromText(text);

        return res.status(200).json({
            success: true,
            message: "Job parsed successfully.",
            data: result,
        });
    } catch (error) {
        console.error(error);

        return res.status(500).json({
            success: false,
            message: "Failed to parse job text.",
        });
    }
};