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

export const parseJobFromUrl = async (
    token: string,
    url: string
) => {
    const response = await api.post(
        "/jobs/url",
        { url },
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    return response.data;
};

export const parseJobFromText = async (
    token: string,
    text: string
) => {
    const response = await api.post(
        "/jobs/text",
        { text },
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    return response.data;
};  