"use client"

import { cookies } from "next/headers";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

interface Todo {
    id: number;
    title: string;
    completed: boolean;
}

function generate_headers(access_token: string | null) {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }
}

export const TodoList = () => {
    const [todos, setTodos] = useState<Todo[]>([]);
    const [newTodo, setNewTodo] = useState("");
    const router = useRouter();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const accessToken = localStorage.getItem("access_token");

    useEffect(() => {
        const fetchTodos = async () => {
            console.log(Date.now());
            // const jwt = cookies().get("access_token");
            setIsLoading(true);
            const jwt = accessToken;
            console.log(jwt?.slice(0, 20) + "...");

            if (!jwt) {
                router.push("/login");
                return
            }
            
            const headers = generate_headers(jwt);
            const response = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/tasks/", { headers });

            if (response.status == 401) {
                router.push("/login");
                return
            }

            if (response.ok) {
                const data = await response.json();
                setTodos(data);
            }

            setIsLoading(false);
            console.log(Date.now());
        }

        fetchTodos();
    }, [])

    const handleAddTodo = async () => {
        if (newTodo.trim()) {
            const id = Date.now();
            const body = { id, title: newTodo.trim(), completed: false }
            setTodos([...todos, body]);
            setNewTodo("");
            
            const headers = generate_headers(accessToken);
            const response = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/tasks/", { 
                headers,
                method: "POST",
                body: JSON.stringify(body),
            });
            const createdTask = await response.json();

            const oldCreatedTodo = todos.find((value) => value.id === id);
            if (oldCreatedTodo) {
                oldCreatedTodo.id = createdTask.id;   
            }
        }
    };

    const handleToggleTodo = async (id: number) => {
        setTodos(
            todos.map((todo) => todo.id == id ? { ...todo, completed: !todo.completed } : todo)
        );
        const headers = generate_headers(accessToken);
        const body = JSON.stringify({ task_id: id });
        const response = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/tasks/complete/", { 
            headers,
            method: "POST",
            body,
        }).catch((error) => {
            console.error(error);
        });
    };

    const handleDeleteTodo = async (id: number) => {
        setTodos(todos.filter((todo) => todo.id !== id));
        const headers = generate_headers(accessToken);
        const response = await fetch(process.env.NEXT_PUBLIC_API_URL + `/api/tasks/${id}/`, { 
            headers,
            method: "DELETE",
        }).catch((error) => {
            console.error(error);
        });
    }

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            handleAddTodo();
        }
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl mb-4">TODO List</h1>
            <div className="flex mb-5">
                <input
                type="text"
                className="border p-2 w-full text-black rounded-md max-w-xl"
                value={newTodo}
                onChange={(e) => setNewTodo(e.target.value)}
                placeholder="Add new todo"
                onKeyDown={handleKeyDown}
                />
                <button
                className="bg-blue-500 text-white p-2 px-5 ml-4 rounded-md"
                onClick={handleAddTodo}
                about="Add task"
                >
                Add
                </button>
            </div>
            <p>{isLoading ? "Loading..." : ""}</p>
            <ul>
                {todos.map((todo) => (
                    <li
                        key={todo.id}
                        className={"flex justify-between p-2 mb-2"}
                    >

                    <span
                    className={`cursor-pointer ${todo.completed ? "line-through" : ""}`}
                    onClick={() => handleToggleTodo(todo.id)}
                    about={todo.completed ? "Task is completed" : "Task is not completed"}
                    >
                    {`${todo.completed ? "✅" : "❌"} ${todo.title}`}
                    </span>

                    <button 
                    className="bg-red-500 text-white px-3 py-0.5 text-[15px] no-underline rounded-md"
                    onClick={() => handleDeleteTodo(todo.id)}
                    about="Delete Task"
                    >
                    Delete
                    </button>
                </li>
                ))}
            </ul>
        </div>
    )
}