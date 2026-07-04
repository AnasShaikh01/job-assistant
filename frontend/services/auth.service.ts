import { api } from "@/lib/api";

class AuthService {
    async me(token: string) {
        const { data } = await api.get("/auth/me", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        return data;
    }
}

export const authService = new AuthService();