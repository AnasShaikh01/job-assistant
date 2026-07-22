import { Router } from "express";
import { upload } from "../../middleware/upload.middleware";
import { uploadJobDescription } from "./jobs.controller";

const router = Router();

router.post(
    "/upload",
    upload.single("job"),
    uploadJobDescription
);

export default router;