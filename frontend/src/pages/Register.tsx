import { useState } from "react";
import { register } from "../utils/auth";


export default function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [avatar, setAvatar] = useState<File | null>(null);
    const [avatarPreview, setAvatarPreview] = useState<string>("");

    const handleRegister = async () => {
        try {
            const formData = new FormData();
            formData.append("username", username)
            formData.append("password", password)
            if (avatar) {
                formData.append("avatar", avatar)
            }
            await register(formData)
            alert("注册成功");
            window.location.href = "/login";
        } catch (e) {
            alert("注册失败");
        }
    }

    return (

        <div className="flex min-h-screen items-center justify-center bg-gray-100">
            <div className="w-96 rounded-xl bg-white p-8 shadow ">
                <h1 className="mb-6 text-2xl font-bold text-center">
                    注册账号
                </h1>
                {/* 头像上传 */}
                <div className="mb-4 flex flex-col items-center gap-3">

                    <div className="mb-4 flex justify-center">

                        <label
                            htmlFor="avatar-upload"
                            className="flex h-24 w-24 cursor-pointer items-center justify-center overflow-hidden rounded-full border-2 border-dashed border-gray-300 bg-gray-100 text-3xl text-gray-400 hover:border-gray-500">
                            {
                                avatarPreview ? (
                                    <img
                                        src={avatarPreview}
                                        className="h-full w-full object-cover"/>) : (
                                    <span>+</span>
                                )
                            }
                        </label>

                        <input
                            id="avatar-upload"
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={
                                e => {
                                    const file =
                                        e.target.files?.[0];

                                    if (file) {
                                        setAvatar(file);
                                        setAvatarPreview(
                                            URL.createObjectURL(file)
                                        );
                                    }
                                }
                            }
                        />
                    </div>
                </div>

                <input className="mb-4 w-full rounded border p-3 "
                    placeholder="用户名"
                    value={username}
                    onChange={
                        e =>
                            setUsername(
                                e.target.value
                            )
                    }
                />

                <input className=" mb-6 w-full rounded border p-3"
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
                    onClick={handleRegister}
                    className="w-full rounded bg-black py-3 text-white"
                >
                    注册
                </button>

                <p className="mt-4 text-center text-sm">
                    已有账号？
                    <a href="/login" className=" ml-1 text-blue-500">
                        登录
                    </a>
                </p>
            </div>
        </div>
    );

}