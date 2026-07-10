import { Request, Response } from "express";
import { getAuth } from "@clerk/express";
import { authService } from "../auth/auth.service";
import { candidateService } from "./candidate.service";

class CandidateController {
    async getProfile(req: Request, res: Response) {
        try {
            const { userId } = getAuth(req);

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    message: "Unauthorized",
                });
            }

            const user = await authService.findByClerkId(userId);

            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: "User not found",
                });
            }

            const profile = await candidateService.getProfile(user.id);

            return res.status(200).json({
                success: true,
                data: profile,
            });
        } catch (error) {
            console.error(error);

            return res.status(500).json({
                success: false,
                message: "Internal Server Error",
            });
        }
    }

    async updateProfile(req: Request, res: Response) {
        try {
            const { userId } = getAuth(req);

            if (!userId) {
                return res.status(401).json({
                    success: false,
                    message: "Unauthorized",
                });
            }

            const user = await authService.findByClerkId(userId);

            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: "User not found",
                });
            }

            const { ckb } = req.body;

            const profile = await candidateService.updateProfile(
                user.id,
                ckb
            );

            return res.status(200).json({
                success: true,
                message: "Candidate profile updated successfully",
                data: profile,
            });
        } catch (error) {
            console.error(error);

            return res.status(500).json({
                success: false,
                message: "Internal Server Error",
            });
        }
    }
}

export const candidateController = new CandidateController();