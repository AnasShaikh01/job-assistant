export interface ResumeUploadResponse {
    message: string;
    resumeMetadata: {
        id: string;
        status: "UPLOADED" | "PROCESSING" | "COMPLETED" | "FAILED";
    };
}