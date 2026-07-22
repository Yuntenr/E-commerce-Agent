import { useState } from "react";
import { login } from "../utils/auth";


export default function Login() {

    const [username, setUsername]= useState("");
    const [password, setPassword]= useState("");

    const handleLogin = async () => {
        try {
            const data = await login(username, password);
            /*
              保存JWT
            */
            localStorage.setItem("user", JSON.stringify(data));
            alert("登录成功");
            /*
              后续跳转Agent页面
            */
            window.location.href = "/chat";
        } catch (e) {
            alert("用户名或密码错误");
        }
    }

    return (
        <div
            className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-96 rounded-xl bg-white p-8 shadow">
                <h1 className=" mb-6 text-2xl font-bold text-center">
                    登录 Agent
                </h1>
                <input
                    className="mb-4 w-full rounded border p-3 "
                    placeholder="用户名"
                    value={username}
                    onChange={
                        e =>
                            setUsername(
                                e.target.value
                            )
                    }
                />

                <input className=" mb-6 w-full rounded border p-3 "
                    type="password"
                    placeholder="密码"
                    value={password}
                    onChange={
                        e =>
                            setPassword(
                                e.target.value
                            )
                    }
                />

                <button
                 onClick={handleLogin}
                 className="w-full rounded bg-black py-3 text-white ">
                    登录
                </button>
                <p className=" mt-4 text-center text-sm">
                    没有账号？
                    <a href="/register" className=" ml-1 text-blue-500 ">
                        注册
                    </a>
                </p>
            </div>
        </div>
    );
}