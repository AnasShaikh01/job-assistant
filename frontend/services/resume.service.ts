import { api } from "@/lib/api";
import { ResumeUploadResponse } from "@/types/resume";

class ResumeService {
    async uploadResume(token: string, file: File): Promise<ResumeUploadResponse> {
        const formData = new FormData();
        formData.append("resume", file);

        const { data } = await api.post<ResumeUploadResponse>(
            "/resume/upload",
            formData,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    // Axios automatically sets the Content-Type to 'multipart/form-data' 
                    // when passing a FormData object.
                },
            }
        );

        return data;
    }
}

export const resumeService = new ResumeService();