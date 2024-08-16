"use client"
import { useRouter } from "next/navigation"

export const NavBar = ({ isLoggedIn, handleLogout }: { isLoggedIn?: boolean, handleLogout?: () => void }) => {
    isLoggedIn ??= localStorage.getItem("access_token") != null;
    
    const router = useRouter();
    return (
        <nav className="bg-gray-900 p-4 fixed w-full flex items-center justify-between">
            <a href="/">
                <h1 className="text-white text-2xl">Todo App</h1>
            </a>
            <div>
                {isLoggedIn ? (
                    <button onClick={handleLogout} className="bg-red-500 text-white p-2 px-3 rounded-md ml-2">
                        Logout
                    </button>
                ) : (
                    <>
                        <button
                            className="bg-blue-500 text-white p-2 rounded-md ml-2"
                            onClick={() => router.push("/login")}
                        >
                            Login
                        </button>
                        <button 
                            className="bg-green-500 text-white p-2 rounded-md ml-2"
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