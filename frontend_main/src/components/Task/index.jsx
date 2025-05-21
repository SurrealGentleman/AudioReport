import React, { useState } from "react";
import { clock, done } from "../../assets";
import { patchTask } from "../../services/taskService";
import { employee } from "../../constants/tables";

const Task = ({ task, updateTasks, setUpdateTasks, user }) => {
  const [showEditStatus, setShowEditStatus] = useState(false);

  const handleChangeStatus = async (status) => {
    try {
      const response = await patchTask(task.id, status);
      setShowEditStatus(false);
      setUpdateTasks(updateTasks + 1);
    } catch (error) {
      alert("Произошла ошибка при изменении статуса задачи");
      console.error("Ошибка изменения статуса задачи: ", error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg relative">
      <img
        className="absolute right-5 hover:bg-brand-grey p-1 rounded-full cursor-pointer"
        src={task.status ? done : clock}
        title={task.status ? "Выполнено" : "В процессе"}
        width={27}
        onClick={() => setShowEditStatus(true)}
      />
      {showEditStatus && (
        <div className="absolute bg-brand-grey rounded-lg right-3 top-14 text-sm shadow-xl">
          <div
            className="hover:bg-brand-blue hover:text-white pt-2 pb-1 px-5 rounded-t-lg cursor-pointer"
            onClick={() => handleChangeStatus(false)}
          >
            В процессе
          </div>
          <div
            className="hover:bg-brand-blue hover:text-white pb-2 pt-1 px-5 rounded-b-lg cursor-pointer"
            onClick={() => handleChangeStatus(true)}
          >
            Выполнена
          </div>
        </div>
      )}
      <div className="space-y-4">
        <div>
          <b>Исполнитель: </b>
          {user?.full_name}
        </div>
        <div>
          <b>Дата назначения: </b>
          {task?.assigned_date}
        </div>
        <div>
          <b>Срок выполнения: </b>
          {task?.due_date}
        </div>
        <div className="bg-brand-purple rounded-lg p-5">{task?.content}</div>
      </div>
    </div>
  );
};

export default Task;
