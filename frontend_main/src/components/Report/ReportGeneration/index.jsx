import React, { useEffect, useState } from "react";
import { getPosts } from "../../../services/postService";
import Dropdown from "../../Dropdown";
import { getDepartments } from "../../../services/departmentService";
import Input from "../../Input";
import { useSelector } from "react-redux";
import { getEmployees } from "../../../services/employeeService";
import Button from "../../Button";
import { generateReport } from "../../../services/meetingService";

const ReportGenegation = () => {
  const isAuthenticated = useSelector((state) => state.global.isAuthenticated);
  const user = useSelector((state) => state.global.user);
  const [posts, setPosts] = useState();
  const [departments, setDepartments] = useState();
  const [employees, setEmployees] = useState();

  const [openPost, setOpenPost] = useState(false);
  const [openDepartment, setOpenDepartment] = useState(false);
  const [openEmployee, setOpenEmployee] = useState(false);

  const [selectPost, setSelectPost] = useState();
  const [selectDepartments, setSelectDepartments] = useState([]);
  const [selectEmployees, setSelectEmployees] = useState([]);
  const [selectFio, setSelectFio] = useState([]);
  const [dateMeeting, setDateMeeting] = useState();
  const [record, setRecord] = useState();

  useEffect(() => {
    if (isAuthenticated) {
      (async () => {
        try {
          const data = await getPosts();
          setPosts(data);
        } catch (error) {
          console.error("Ошибка при получении должностей:", error);
        }
      })();
      (async () => {
        try {
          const data = await getDepartments();
          setDepartments(data);
        } catch (error) {
          console.error("Ошибка при получении отделов:", error);
        }
      })();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    console.log(employees);
    const resultFio = selectEmployees
      .map((id) => employees.find((emp) => emp.id === id))
      .filter(Boolean) // убираем undefined, если id не найден
      .map((emp) => emp.full_name);

    setSelectFio(resultFio);
  }, [selectEmployees]);

  useEffect(() => {
    (async () => {
      try {
        const params = {};
        if (selectDepartments?.id !== undefined)
          params.department = selectDepartments.id;
        if (selectPost?.id !== undefined) params.post = selectPost.id;

        const data = await getEmployees(params);
        setEmployees(data);
      } catch (error) {
        console.error("Ошибка при получении сотрудников:", error);
      }
    })();
  }, [isAuthenticated, selectDepartments, selectPost]);

  const handleChangeFile = (e) => {
    setRecord(e.target.files[0]);
  };

  const handleCreateReport = async () => {
    console.log("create", selectEmployees);

    if (selectEmployees && dateMeeting && record) {
      const employees = selectEmployees.map((item) => ({
        employee_id: item,
        is_responsible: item === user.id,
      }));

      const dataJson = {
        participants: employees,
        meeting_date: dateMeeting,
      };

      const formData = new FormData();
      formData.append("audio", record);
      formData.append("data", JSON.stringify(dataJson));
      console.log(formData);

      try {
        const data = await generateReport(formData);
        console.log(data);
      } catch (error) {
        console.error("Ошибка генерации отчета: ", error);
      }
    }
  };

  return (
    <div className="bg-white mt-10 rounded-lg p-7 text-lg flex flex-col">
      <div className="space-y-3 mt-3">
        <div className="border p-2 rounded-lg">
          <p className="text-sm mb-2">Фильтрация участников совещания</p>
          <div className="flex gap-44">
            {departments && (
              <Dropdown
                title="Отдел"
                dropOpen={openDepartment}
                setDropOpen={setOpenDepartment}
                objects={departments}
                // placeholder="Выберите отдел"
                onChangeSelect={setSelectDepartments}
                clearable
                searchable
                showArrow
                color="bg-brand-grey"
              />
            )}
            {posts && (
              <div className="ml-2">
                <Dropdown
                  title="Должность"
                  dropOpen={openPost}
                  setDropOpen={setOpenPost}
                  objects={posts}
                  onChangeSelect={setSelectPost}
                  clearable
                  searchable
                  showArrow
                  color="bg-brand-grey"
                />
              </div>
            )}
          </div>
        </div>
        <div className="flex pl-2">
          <div className="flex flex-col gap-4 w-1/2">
            <div className="mt-0/5 w-[190px]">
              {employees && (
                <Dropdown
                  title="Участники совещания"
                  placeholder="Выбрать"
                  dropOpen={openEmployee}
                  setDropOpen={setOpenEmployee}
                  objects={employees}
                  // placeholder="Выберите сотрудников"
                  onChangeSelect={setSelectEmployees}
                  clearable
                  searchable
                  showArrow
                  multiple
                  displayProperty="full_name"
                  color="bg-brand-grey"
                />
              )}
            </div>
            <div className="mt-5 w-[250px]">
              <p className="text-xs text-gray-500">Дата проведения совещания</p>
              <div className="text-xs">
                <Input
                  type="date"
                  inputStyle="py-2 mt-0"
                  onChange={(e) => setDateMeeting(e.target.value)}
                />
              </div>
            </div>
          </div>
          <div
            className={`mt-3 space-y-1 ${
              selectFio.length > 0 ? "pl-14" : "pl-24"
            } text-sm text-gray-500`}
          >
            {selectFio.length > 0 ? (
              selectFio?.map((item) => <div>{item}</div>)
            ) : (
              <div>Участники совещания еще не были выбраны</div>
            )}
          </div>
        </div>
      </div>
      <div className="mt-5 w-[39%] ml-2">
        <div className="text-xs text-gray-500">Запись совещания</div>
        <Input type="file" inputStyle="text-xs" onChange={handleChangeFile} />
      </div>

      <div className="self-center mt-6">
        <Button
          text="Сгенерировать отчет"
          buttonStyle="text-sm"
          onClick={handleCreateReport}
        />
      </div>
    </div>
  );
};

export default ReportGenegation;
