import React, { useEffect, useState } from "react";
import { getPosts } from "../../../services/postService";
import Dropdown from "../../Dropdown";
import { getDepartments } from "../../../services/departmentService";
import Input from "../../Input";
import { useSelector } from "react-redux";
import { getEmployees } from "../../../services/employeeService";
import Button from "../../Button";
import { generateReport } from "../../../services/meetingService";
import { trackPromise, usePromiseTracker } from "react-promise-tracker";
import { example } from "../../../constants/example";
import TaskEmployee from "../TaskEmployee";

const area = "report";
const ReportGenegation = () => {
  const isAuthenticated = useSelector((state) => state.global.isAuthenticated);
  const user = useSelector((state) => state.global.user);
  const { promiseInProgress } = usePromiseTracker({ area });

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

  const [report, setReport] = useState(example);
  const [keyQuestions, setKeyQuestions] = useState();

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

  useEffect(() => {
    if (report?.key_questions) {
      setKeyQuestions(
        report.key_questions
          .map((question, index) => `${index + 1}. ${question}`)
          .join("\n")
      );
    }
  }, [report]);

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
        const data = await trackPromise(generateReport(formData), area);
        setReport(data);
        console.log(data);
      } catch (error) {
        console.error("Ошибка генерации отчета: ", error);
      }
    }
  };

  return (
    <div className="bg-white my-10 rounded-lg p-7 text-lg flex flex-col">
      {report ? (
        <>
          {!promiseInProgress ? (
            <>
              <div className="space-y-3 mt-3">
                <div className="border p-2 rounded-lg">
                  <p className="text-sm mb-2">
                    Фильтрация участников совещания
                  </p>
                  <div className="flex gap-44">
                    {departments && (
                      <Dropdown
                        title="Отдел"
                        dropOpen={openDepartment}
                        setDropOpen={setOpenDepartment}
                        objects={departments}
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
                      <p className="text-xs text-gray-500">
                        Дата проведения совещания
                      </p>
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
                <Input
                  type="file"
                  inputStyle="text-xs"
                  onChange={handleChangeFile}
                />
              </div>

              <div className="self-center mt-6">
                <Button
                  text="Сгенерировать отчет"
                  buttonStyle="text-sm"
                  onClick={handleCreateReport}
                />
              </div>
            </>
          ) : (
            <div className="self-center h-36 flex flex-col items-center">
              <p>Генерируется отчет, пожалуйста, подождите…</p>
              <div className="relative top-9 w-[76px] h-[50px] my-loader">
                <span
                  className="absolute inset-0 m-auto w-5 h-5 rounded-full bg-[#7176B9] my-spin"
                  style={{ transformOrigin: "-24px 50%" }}
                ></span>
                <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-[#7176B9]"></span>
              </div>
            </div>
          )}
        </>
      ) : (
        <div>
          <div className="flex justify-between mb-7">
            <div className="font-semibold text-xl">Редактирование отчета</div>
            <div
              className="text-xs flex justify-end items-center gap-2"
              title="Дата проведения совещания"
            >
              <div className="bg-brand-purple py-1 px-2 rounded-lg ">
                {report.meeting_date}
              </div>
            </div>
          </div>

          <div className="space-y-7">
            <div>
              <div className="w-full flex mt-3 items-center text-lg whitespace-nowrap mb-1">
                <p>Тема совещания</p>
                <hr className="border-0.5 w-full ml-2" />
              </div>
              <textarea
                className="bg-brand-grey rounded-lg px-3 py-1 resize-none text-sm h-14"
                cols={82}
                rows={1}
                value={report.topic}
                id="autoResizeTopic"
              />
            </div>
            <div>
              <div className="w-full flex mt-3 items-center text-lg whitespace-nowrap mb-1">
                <p>Участники</p>
                <hr className="border-0.5 w-full ml-2" />
              </div>
              <div className="text-sm">
                {report.participants.map((person) => (
                  <div>
                    {person.last_name} {person.first_name} {person.patronymic}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="w-full flex mt-3 items-center text-lg whitespace-nowrap mb-1">
                <p>Ключевые вопросы</p>
                <hr className="border-0.5 w-full ml-2" />
              </div>
              <textarea
                className="bg-brand-grey rounded-lg px-3 py-1 resize-none text-sm"
                rows={report.key_questions.length}
                cols={82}
                value={keyQuestions}
              />
            </div>
            <div>
              <div className="w-full flex mt-3 items-center text-lg whitespace-nowrap mb-1">
                <p>Содержание</p>
                <hr className="border-0.5 w-full ml-2" />
              </div>
              <textarea
                className="bg-brand-grey rounded-lg px-3 py-1 resize-none text-sm h-32"
                cols={82}
                rows={1}
                value={report.summary}
                id="autoResize"
              />
            </div>
            <table className="my-7 w-full text-sm">
              <tr className="bg-brand-purple rounded-t-lg">
                <th className="border w-3/6 py-2">Задача</th>
                <th className="border w-1/4">Сотрудник</th>
                <th>Срок выполнения</th>
              </tr>
              {report.tasks.map((task, index) => (
                <TaskEmployee
                  task={task}
                  report={report}
                  indexTask={index}
                  setReport={setReport}
                />
              ))}
            </table>
            <div className="flex justify-center">
              <Button
                text="Сохранить отчет"
                buttonStyle="text-sm"
                onClick={handleCreateReport}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportGenegation;
