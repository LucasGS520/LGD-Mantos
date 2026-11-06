import { request } from "../../shared/api/http";
import { Session } from "./session";
export const api = {
  login: async (password: string) => {
    const data = await request<{ token: string }>("/auth/login", "POST", {
      password,
    });
    Session.save(data.token);
    return data.token;
  },
};
