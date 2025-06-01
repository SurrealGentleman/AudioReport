import React, { useState, useEffect } from "react";
import Input from "../../Input";
import Button from "../../Button";
import Table from "./Table";
import {
  getDepartments,
  postDepartment,
} from "../../../services/departmentService";
import { department } from "../../../constants/tables";

const DepartmentModule = () => {
  const [nameDepartment, setNameDepartment] = useState();
  const [allDepartments, setAllDepartments] = useState();
  const [updateDepartments, setUpdateDepartments] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const data = await getDepartments();
        setAllDepartments(data);
      } catch (error) {
        console.error("Ошибка при получении отделов:", error);
      }
    })();
  }, []);

  const handleAddDepartment = async (e) => {
    e.preventDefault();
    try {
      const response = await postDepartment(nameDepartment);
      setNameDepartment(null);
      setAllDepartments(response);
    } catch (error) {
      console.error("Ошибка добавления отдела: ", error);
    }
  };

  return (
    <div>
      <div className="bg-white p-6 rounded-lg space-y-5">
        <div className="w-2/3">
          <Input
            type="text"
            value={nameDepartment}
            title="Наименование"
            onChange={(e) => setNameDepartment(e.target.value)}
          />
        </div>
        <Button
          text="Добавить отдел"
          buttonStyle="text-sm"
          onClick={handleAddDepartment}
        />
      </div>
      <Table
        headers={department}
        items={allDepartments}
        updateDepartments={updateDepartments}
        setUpdateDepartments={setUpdateDepartments}
      />
    </div>
  );
};

export default DepartmentModule;
