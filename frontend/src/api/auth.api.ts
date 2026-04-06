import client from "./client";
import type { LoginResponse } from "@/types/user.types";
import type { ApiResponse } from "@/types/api.types";

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await client.post<ApiResponse<LoginResponse>>(
      "auth/login/",
      { email, password },
    );

    return response.data.data;
  },

  logout: async (refreshToken: string) => {
    await client.post("/auth/login/", { refresh_token: refreshToken });
  },

  getMe: async () => {
    const response = await client.get("/auth/me");
    return response.data.data;
  },

  changePassword: async (oldPassword: string, newPassword: string) => {
    await client.post("/auth/password/change/", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
