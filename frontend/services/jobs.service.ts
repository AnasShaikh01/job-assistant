import { api } from "@/lib/api";

export const uploadJobDescription = async (
    token: string,
    file: File
) => {
    const formData = new FormData();

    formData.append("job", file);

    const response = await api.post(
        "/jobs/upload",
        formData,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};