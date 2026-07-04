import multer from "multer";

const storage = multer.memoryStorage();

export const upload = multer({
    storage,

    limits: {
        fileSize: 5 * 1024 * 1024, // 5 MB
    },

    fileFilter: (_req, file, cb) => {
        const allowedMimeTypes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ];

        if (!allowedMimeTypes.includes(file.mimetype)) {
            return cb(new Error("Only PDF, DOC and DOCX files are allowed."));
        }

        cb(null, true);
    },
});