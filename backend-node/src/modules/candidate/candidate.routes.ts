import { Router } from "express";
import { requireAuth } from "@clerk/express";
import { candidateController } from "./candidate.controller";

const router = Router();

router.get(
    "/profile",
    requireAuth(),
    candidateController.getProfile
);

router.patch(
    "/profile",
    requireAuth(),
    candidateController.updateProfile
);

export default router;