import { NavBar } from "@/components/NavBar";
import { TodoList } from "@/components/TodoList";

export default function Home() {
    return (
        <>
            <NavBar />
            <div className="bg-gray-700 min-h-screen flex justify-center items-center">
                <TodoList />
            </div>
        </>
    )
}