import React, { useEffect, useState } from "react";
import { getTasks } from "../services/taskService";
import Task from "../components/Task";
import { useSelector } from "react-redux";

const TasksPage = () => {
  const user = useSelector((state) => state.global.user);
  const [allTasks, setAllTasks] = useState();
  const [updateTasks, setUpdateTasks] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const data = await getTasks(user.id);
        setAllTasks(data);
      } catch (error) {
        console.error("Ошибка при получении задач:", error);
      }
    })();
  }, [updateTasks]);

  return (
    <div className="w-2/3">
      <p className="text-3xl">Задачи</p>
      <div className="space-y-8 mt-5">
        {!allTasks && <p className="text-gray-700">У вас нет задач</p>}
        {allTasks?.map((task) => {
          return (
            <Task
              user={user}
              key={task.id}
              task={task}
              updateTasks={updateTasks}
              setUpdateTasks={setUpdateTasks}
            />
          );
        })}
      </div>
    </div>
  );
};

export default TasksPage;
