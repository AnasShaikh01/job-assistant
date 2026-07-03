import { Router } from "express";
import { getCurrentUser } from "./auth.controller";

const router = Router();

router.get("/me", getCurrentUser);

export default router;