import { Router } from "express";
import { upload } from "../../middleware/upload.middleware";
import {
    uploadJobDescription,
    parseJobFromUrl,
    parseJobFromText,
} from "./jobs.controller";

const router = Router();

router.post(
    "/upload",
    upload.single("job"),
    uploadJobDescription
);

router.post(
    "/url",
    parseJobFromUrl
);

router.post(
    "/text",
    parseJobFromText
);

export default router;