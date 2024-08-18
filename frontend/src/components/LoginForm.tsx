"use client"

import { redirect, RedirectType, useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

type payloadType = {
    username: FormDataEntryValue | null;
    password: FormDataEntryValue | null;
    email?: FormDataEntryValue | null;
};

type submitReturnType = { ok: boolean, tokens?: { access: string, refresh: string }, error: string | Record<string, any> | null }
type loginFormType = { submitFunc: (payload: payloadType) => Promise<submitReturnType>, addEmailField?: boolean, buttonText?: string };
export const LoginForm = ({ submitFunc, addEmailField = false, buttonText = "Login" }: loginFormType) => {
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [errors, setErrors] = useState<string>("");
    const router = useRouter();

    const submit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsLoading(true);
        const formData = new FormData(event.currentTarget);

        const payload: payloadType = {
            username: formData.get("username"),
            password: formData.get("password"),
        };
        if (formData.get("email")) {
            payload.email = formData.get("email");
        }
        
        try {
            const submitResult = await submitFunc(payload);
            if (submitResult.ok && submitResult.tokens) {
                setErrors("");
                const tokens = submitResult.tokens;
                localStorage.setItem("access_token", tokens.access);
                localStorage.setItem("refresh_token", tokens.refresh);
                router.push("/");
            } else {
                const error = submitResult.error;
                const fieldUnique = "This field must be unique.";
                if (error && typeof error === "object") {
                    console.log(error.username, fieldUnique in error.username, error.username.includes(fieldUnique))
                    if (error.username.includes(fieldUnique)) {
                        console.log("Username aldready exists")
                        setErrors("User with this username already registred");
                        console.log(errors);
                    }

                    if (error.email.includes(fieldUnique)) {
                        setErrors("User with this email already registred");
                    }
                }
                
                if (!errors) {
                    setErrors("Unnexpected error");
                } 
            }
        } catch (error) {
            console.error(error);
            setErrors("Unnexpected error");
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <>
            {/* <h2>Login Form</h2> */}
            <div id="form" className="bg-gray-800 border border-gray-500 rounded-lg flex p-5 py-6 min-w-[23%]">
                <form onSubmit={submit} className="flex flex-col w-full px-12">
                    <label htmlFor="username">Username</label>
                    <input required type="text" id="username" name="username" about="Username" className="rounded-md text-black p-1 py-1.5 my-1 mb-7" />

                    {addEmailField && (
                        <>
                            <label htmlFor="email">Email</label>
                            <input required type="email" id="email" about="Email" name="email" className="rounded-md text-black p-1 py-1.5 my-1 mb-7" />
                        </>
                    )}
                    

                    <label htmlFor="password">Password</label>
                    <input required type="password" id="password" name="password" about="Password" className="rounded-md text-black p-1 py-1.5 my-1 mb-8" />

                    <button type="submit" disabled={isLoading} className="px-2 py-3 bg-gray-900 rounded-lg mx-10 mb-2 disabled:text-gray-200 disabled:bg-gray-950">
                        {buttonText}
                    </button>

                    <div className="flex items-center justify-center flex-col">
                        <p>{isLoading ? "Loading..." : ""}</p>
                        <p className="text-red-600">{errors}</p>
                    </div>
                </form>
            </div>
        </>
    )
}