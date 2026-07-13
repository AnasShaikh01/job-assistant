import { Router } from "express";

import healthRoutes from "./modules/health/health.routes";
import authRoutes from "./modules/auth/auth.routes";
import resumeRoutes from "./modules/resume/resume.routes";
import candidateRoutes from "./modules/candidate/candidate.routes";

const router = Router();

router.use("/health", healthRoutes);
router.use("/auth", authRoutes);
router.use("/resume", resumeRoutes);
router.use("/candidate", candidateRoutes);

export default router;