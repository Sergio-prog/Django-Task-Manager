"use client"

import { LoginForm } from "@/components/LoginForm";
import { NavBar } from "@/components/NavBar";

export default function Login() {
    const submitFunc = async (payload: object) => {
        const url = process.env.NEXT_PUBLIC_API_URL + "/api/auth/login/";
        const response = await fetch(url, {
            method: "POST",
            body: JSON.stringify(payload),
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        
        if (response.ok) {
            const expiryDate = 30 * 60 * 60 * 24 * 1000;
            // cookies().set("access_token", data.access, { expires: expiryDate });
            // cookies().set("refresh_token", data.refresh, { expires: expiryDate });
            const tokens = { access: data.access as string, refresh: data.refresh as string };
            return { ok: true, error: null, tokens }
        } else {
            return { ok: false, error: data };
        }
    }

    return (
        <>
            <NavBar titleOfPage="Login" />
            <div className="min-h-screen flex justify-center items-center bg-gray-700">
                <LoginForm submitFunc={submitFunc} />
            </div>
        </>
    )
}