
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
export async function login(
    username: string,
    password: string
) {

    const response = await fetch(
        `${API_BASE_URL}/E-commerce/login`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        }
    );

    if (!response.ok) {
        throw new Error("登录失败");
    }
    return await response.json();
}

export async function register(
    formData: FormData
) {
    const response = await fetch(
        `${API_BASE_URL}/E-commerce/register`,
        {
            method: "POST",
            body: formData
        }
    );

    if (!response.ok) {
        throw new Error("注册失败");
    }
    return await response.json();
}