import React, { useEffect, useState } from "react";
import { getPosts } from "../../../services/postService";
import { getDepartments } from "../../../services/departmentService";
import { getEmployees, postEmployee } from "../../../services/employeeService";
import Button from "../../Button";
import Dropdown from "../../Dropdown";
import Input from "../../Input";
import { employee } from "../../../constants/tables";
import Table from "./Table";
import { check, square } from "../../../assets";

const EmployeeModule = () => {
  const [allDepartment, setAllDepartment] = useState();
  const [allPost, setAllPost] = useState();
  const [allEmployee, setAllEmployee] = useState();
  const [updateEmployees, setUpdateEmployees] = useState(0);

  const [openDepartment, setOpenDepartment] = useState(false);
  const [openPost, setOpenPost] = useState(false);

  const [selectDepartment, setSelectDepartment] = useState();
  const [selectPost, setSelectPost] = useState();

  const [newLastName, setNewLastName] = useState();
  const [newFirstName, setNewFirstName] = useState();
  const [newPatronymic, setNewPatromic] = useState();
  const [newEmail, setNewEmail] = useState();
  const [newPassword, setNewPassword] = useState();
  const [isAdmin, setIsAdmin] = useState(false);

  const [errorValid, setErrorValid] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await getEmployees();
        setAllEmployee(data);
      } catch (error) {
        console.error("Ошибка при получении должностей:", error);
      }
    })();
  }, [updateEmployees]);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPosts();
        setAllPost(data);
      } catch (error) {
        console.error("Ошибка при получении должностей:", error);
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const data = await getDepartments();
        setAllDepartment(data);
      } catch (error) {
        console.error("Ошибка при получении отделов:", error);
      }
    })();
  }, []);

  const handleAddEmployee = async () => {
    if (!newLastName || !newEmail || !newFirstName || !newPassword) {
      setErrorValid(true);
      return;
    }

    const dataJson = {
      department_id: selectDepartment.id,
      post_id: selectPost.id,
      password: newPassword,
      email: newEmail,
      first_name: newFirstName,
      last_name: newLastName,
      patronymic: newPatronymic,
      is_admin: isAdmin,
    };

    try {
      console.log(dataJson);
      const data = await postEmployee(dataJson);
      setAllEmployee(data);
      setSelectDepartment(undefined);
      setSelectPost(undefined);
      setNewPassword(undefined);
      setNewEmail(undefined);
      setNewFirstName(undefined);
      setNewLastName(undefined);
      setNewPatromic(undefined);
      setIsAdmin(false);
    } catch (error) {
      console.error("Ошибка добавления отдела: ", error);
    }
  };

  return (
    <div>
      <div className="bg-white p-6 rounded-lg flex flex-col">
        <div className="flex gap-20">
          {allDepartment && (
            <Dropdown
              title="Отдел"
              dropOpen={openDepartment}
              setDropOpen={setOpenDepartment}
              objects={allDepartment}
              // placeholder="Выберите отдел"
              onChangeSelect={setSelectDepartment}
              clearable
              searchable
              showArrow
              validationError={errorValid}
            />
          )}
          {allPost && (
            <Dropdown
              title="Должность"
              dropOpen={openPost}
              setDropOpen={setOpenPost}
              objects={allPost}
              onChangeSelect={setSelectPost}
              clearable
              searchable
              showArrow
              validationError={errorValid}
            />
          )}
        </div>
        <div className="flex gap-7 mt-4">
          <div className="w-full">
            <Input
              titleStyle="text-base"
              validationError={errorValid}
              type="text"
              title="Фамилия"
              onChange={(e) => setNewLastName(e.target.value)}
            />
          </div>
          <div className="w-full">
            <Input
              titleStyle="text-base"
              validationError={errorValid}
              type="text"
              title="Имя"
              onChange={(e) => setNewFirstName(e.target.value)}
            />
          </div>
        </div>
        <div className="w-full mt-2">
          <Input
            titleStyle="text-base"
            type="text"
            title="Отчество"
            onChange={(e) => setNewPatromic(e.target.value)}
          />
        </div>
        <div className="flex gap-7 mt-10">
          <div className="w-full">
            <Input
              titleStyle="text-base"
              validationError={errorValid}
              type="text"
              title="Почта"
              onChange={(e) => setNewEmail(e.target.value)}
            />
          </div>
          <div className="w-full">
            <Input
              titleStyle="text-base"
              validationError={errorValid}
              type="text"
              title="Пароль"
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>
        </div>
        <div className="flex gap-2 items-center mt-3 text-sm">
          <img
            src={isAdmin ? check : square}
            width={25}
            onClick={() => setIsAdmin(!isAdmin)}
          />
          <p>Сотрудник является администратором</p>
        </div>

        <div className="self-center mt-7">
          <Button
            text="Добавить сотрудника"
            buttonStyle="text-sm"
            onClick={handleAddEmployee}
          />
        </div>
      </div>
      <Table
        headers={employee}
        items={allEmployee}
        updateEmployees={updateEmployees}
        setUpdateEmployees={setUpdateEmployees}
      />
    </div>
  );
};

export default EmployeeModule;
