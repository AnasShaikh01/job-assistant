import { Router } from "express";
import { upload } from "../../middleware/upload.middleware";
import { uploadResume } from "./resume.controller";

const router = Router();

router.post(
    "/upload",
    upload.single("resume"),
    uploadResume
);

export default router;