"use client"
import { useRouter } from "next/navigation"

export const NavBar = ({ titleOfPage, isLoggedIn, handleLogout }: { titleOfPage?: string, isLoggedIn?: boolean, handleLogout?: () => void }) => {
    isLoggedIn ??= localStorage.getItem("access_token") != null;
    handleLogout ??= () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push("/login");
    }
    
    const router = useRouter();
    return (
        <nav className="bg-gray-900 p-4 fixed w-full flex items-center justify-between">
            <a href="/">
                <h1 className="text-white font-medium text-2xl">Todo App</h1>
            </a>

            {titleOfPage && (
                <h1 className="text-slate-200 font-semibold text-2xl">
                    {titleOfPage}
                </h1>
            )}

            <div>
                {isLoggedIn ? (
                    <button onClick={handleLogout} className="bg-red-500 text-white p-2 px-3 rounded-md ml-2">
                        Logout
                    </button>
                ) : (
                    <>
                        <button
                            className="bg-blue-500 text-white p-2 px-3 text-sm rounded-md"
                            onClick={() => router.push("/login")}
                        >
                            Login
                        </button>
                        <button 
                            className="bg-green-500 text-white p-2 px-3 text-sm rounded-md ml-4"
                            onClick={() => router.push("/register")}
                        >
                            Register
                        </button>
                    </>
                )}
            </div>
        </nav>
    )
}