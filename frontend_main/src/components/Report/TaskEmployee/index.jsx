import React, { useEffect, useState } from "react";
import Dropdown from "../../Dropdown";
import Input from "../../Input";

const TaskEmployee = ({ task, report, indexTask, setReport }) => {
  const [openSelect, setOpenSelect] = useState(false);
  const [taskEmployee, setTaskEmployee] = useState();
  const [taskDeadline, setTaskDeadline] = useState();
  const [participants, setParticipants] = useState();

  useEffect(() => {
    setParticipants(report.participants);
    setTaskEmployee(task?.employee_id);

    if (task.deadline) {
      const [day, month, year] = task?.deadline.split(".");
      setTaskDeadline(
        `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`
      );
    }
  }, []);

  useEffect(() => {
    const updatedTasks = report.tasks.map((task, index) =>
      index === indexTask ? { ...task, employee_id: taskEmployee } : task
    );

    setReport({ ...report, tasks: updatedTasks });
  }, [taskEmployee]);

  return (
    <tr>
      <td className="border py-2 px-1">{task?.content}</td>
      <td className="border-b py-2 px-1">
        <div className="w-2/3 ml-2">
          <Dropdown
            placeholder="Выбрать"
            dropOpen={openSelect}
            setDropOpen={setOpenSelect}
            objects={participants}
            onChangeSelect={setTaskEmployee}
            selectedOptionValue={taskEmployee}
            clearable
            searchable
            showArrow
            displayProperty="last_name"
            color="bg-brand-grey"
            classNameArrow="-right-6"
            classNameCross="-right-[5px]"
          />
        </div>
      </td>
      <td className="border px-4 pb-1">
        <Input type="date" value={taskDeadline} />
      </td>
    </tr>
  );
};

export default TaskEmployee;
