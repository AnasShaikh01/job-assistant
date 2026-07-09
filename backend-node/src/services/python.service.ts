import axios from "axios";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

class PythonService {
    async parseResume(resumeFileId: string, fileUrl: string, filename: string) {
        try {
            const response = await axios.post(
                `${PYTHON_API_URL}/api/v1/resume/parse`, 
                {
                    resume_file_id: resumeFileId,
                    file_url: fileUrl,
                    filename: filename,
                },
                {
                    timeout: 60000 // 60-second timeout for large PDFs
                }
            );

            return response.data;
        } catch (error: any) {
            console.error("Error communicating with Python API:", error?.response?.data || error.message);
            throw error;
        }
    }
}

export const pythonService = new PythonService();