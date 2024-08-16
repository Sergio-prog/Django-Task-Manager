"use client"

import { cookies } from "next/headers";
import { redirect, RedirectType, useRouter } from "next/navigation";
import { Router } from "next/router";
import { FormEvent, useState } from "react";

export const LoginForm = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [errors, setErrors] = useState<string>("");
    const router = useRouter();

    const submit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsLoading(true);
        const formData = new FormData(event.currentTarget);
        const url = process.env.NEXT_PUBLIC_API_URL + "/api/auth/login/";
        console.log(formData, url);
        const payload = {
            username: formData.get("username"),
            password: formData.get("password"),
        };

        console.log(payload);
        
        try {
            const response = await fetch(url, {
                method: "POST",
                body: JSON.stringify(payload),
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const data = await response.json();
            console.log(data);
            
            if (response.ok) {
                setErrors("");
                const expiryDate = 30 * 60 * 60 * 24 * 1000;
                // cookies().set("access_token", data.access, { expires: expiryDate });
                // cookies().set("refresh_token", data.refresh, { expires: expiryDate });
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                // redirect("/");
                router.push("/");
            } else {
                setErrors(data?.detail);
            }
        } catch (error) {
            console.log("hey");
            console.error(error);
            console.log("hey2");
            setErrors("Unnexpected error");
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <>
            {/* <h2>Login Form</h2> */}
            <div id="form" className="bg-gray-800 border border-gray-500 rounded-lg flex p-5 min-w-[23%]">
                <form onSubmit={submit} className="flex flex-col w-full px-12">
                    <label htmlFor="username">Username</label>
                    <input type="text" id="username" name="username" about="Username" className="rounded-md text-black p-1 py-1.5 my-1 mb-6" />

                    {/* <label htmlFor="email">Email</label>
                    <input type="email" id="email" about="Email" name="email" className="rounded-md text-black p-1 py-1.5 my-1 mb-6" /> */}

                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" name="password" about="Password" className="rounded-md text-black p-1 py-1.5 my-1 mb-8" />

                    <button type="submit" disabled={isLoading} className="p-2 py-3 bg-gray-900 rounded-md mx-10 mb-2 disabled:text-gray-200 disabled:bg-gray-950">Login</button>

                    <div className="flex items-center justify-center flex-col">
                        <p>{isLoading ? "Loading..." : ""}</p>
                        <p className="text-red-600">{errors}</p>
                    </div>

                    {/* <ul >
                        {errors.map((error) => (
                            <li className="text-red-600">{error}</li>
                        ))}
                    </ul> */}
                </form>
            </div>
        </>
    )
}