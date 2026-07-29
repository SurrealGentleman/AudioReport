import { useEffect, useState } from "react";

import { getEmployees } from "../services/employeeService";
import {
  getDepartments,
  getPositions,
} from "../services/directoryService";
import { generateReport } from "../services/meetingService";

function getErrorMessage(error) {
  const responseData = error.response?.data;

  if (!responseData) {
    return "Не удалось связаться с сервером.";
  }

  if (typeof responseData === "string") {
    return responseData;
  }

  const firstMessage = Object.values(responseData).flat()[0];

  return firstMessage
    ? String(firstMessage)
    : "Не удалось сформировать отчёт.";
}

function HomePage() {
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);
  const [employees, setEmployees] = useState([]);

  const [departmentId, setDepartmentId] = useState("");
  const [positionId, setPositionId] = useState("");
  const [participantIds, setParticipantIds] = useState([]);
  const [responsibleId, setResponsibleId] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [audioFile, setAudioFile] = useState(null);

  const [report, setReport] = useState(null);
  const [isLoadingDirectories, setIsLoadingDirectories] = useState(true);
  const [isLoadingEmployees, setIsLoadingEmployees] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignoreResult = false;

    async function loadDirectories() {
      try {
        const [departmentData, positionData] = await Promise.all([
          getDepartments(),
          getPositions(),
        ]);

        if (!ignoreResult) {
          setDepartments(departmentData);
          setPositions(positionData);
        }
      } catch {
        if (!ignoreResult) {
          setError("Не удалось загрузить отделы и должности.");
        }
      } finally {
        if (!ignoreResult) {
          setIsLoadingDirectories(false);
        }
      }
    }

    loadDirectories();

    return () => {
      ignoreResult = true;
    };
  }, []);

  useEffect(() => {
    let ignoreResult = false;

    async function loadEmployees() {
      setIsLoadingEmployees(true);

      const params = {};

      if (departmentId) {
        params.department = departmentId;
      }

      if (positionId) {
        params.position = positionId;
      }

      try {
        const data = await getEmployees(params);

        if (!ignoreResult) {
          setEmployees(data);
        }
      } catch {
        if (!ignoreResult) {
          setError("Не удалось загрузить сотрудников.");
        }
      } finally {
        if (!ignoreResult) {
          setIsLoadingEmployees(false);
        }
      }
    }

    loadEmployees();

    return () => {
      ignoreResult = true;
    };
  }, [departmentId, positionId]);

  function handleParticipantsChange(event) {
    const selectedIds = Array.from(
      event.target.selectedOptions,
      (option) => option.value
    );

    setParticipantIds(selectedIds);

    if (!selectedIds.includes(responsibleId)) {
      setResponsibleId("");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!audioFile) {
      setError("Выберите аудиозапись.");
      return;
    }

    if (participantIds.length === 0) {
      setError("Выберите хотя бы одного участника.");
      return;
    }

    if (!responsibleId) {
      setError("Выберите ответственного участника.");
      return;
    }

    setError("");
    setReport(null);
    setIsGenerating(true);

    const participants = participantIds.map((id) => ({
      employee_id: Number(id),
      is_responsible: id === responsibleId,
    }));

    const formData = new FormData();

    formData.append("audio", audioFile);
    formData.append(
      "data",
      JSON.stringify({
        meeting_date: meetingDate,
        participants,
      })
    );

    try {
      const generatedReport = await generateReport(formData);
      setReport(generatedReport);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsGenerating(false);
    }
  }

  const selectedEmployees = employees.filter((employee) =>
    participantIds.includes(String(employee.id))
  );

  return (
    <section>
      <h1>Формирование отчёта</h1>

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      <form
        className="uk-card uk-card-default uk-card-body"
        onSubmit={handleSubmit}
      >
        <div className="uk-grid uk-grid-small uk-child-width-1-2@m">
          <div>
            <label className="uk-form-label" htmlFor="department">
              Фильтр по отделу
            </label>

            <select
              className="uk-select"
              id="department"
              value={departmentId}
              onChange={(event) => setDepartmentId(event.target.value)}
              disabled={isLoadingDirectories}
            >
              <option value="">Все отделы</option>

              {departments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="uk-form-label" htmlFor="position">
              Фильтр по должности
            </label>

            <select
              className="uk-select"
              id="position"
              value={positionId}
              onChange={(event) => setPositionId(event.target.value)}
              disabled={isLoadingDirectories}
            >
              <option value="">Все должности</option>

              {positions.map((position) => (
                <option key={position.id} value={position.id}>
                  {position.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="uk-margin">
          <label className="uk-form-label" htmlFor="participants">
            Участники
          </label>

          <select
            className="uk-select"
            id="participants"
            multiple
            size="7"
            value={participantIds}
            onChange={handleParticipantsChange}
            disabled={isLoadingEmployees}
            required
          >
            {employees.map((employee) => (
              <option key={employee.id} value={employee.id}>
                {employee.full_name}
              </option>
            ))}
          </select>

          <div className="uk-text-meta">
            Для выбора нескольких сотрудников удерживайте Ctrl.
          </div>
        </div>

        <div className="uk-margin">
          <label className="uk-form-label" htmlFor="responsible">
            Ответственный за совещание
          </label>

          <select
            className="uk-select"
            id="responsible"
            value={responsibleId}
            onChange={(event) => setResponsibleId(event.target.value)}
            required
          >
            <option value="">Выберите ответственного</option>

            {selectedEmployees.map((employee) => (
              <option key={employee.id} value={employee.id}>
                {employee.full_name}
              </option>
            ))}
          </select>
        </div>

        <div className="uk-grid uk-grid-small uk-child-width-1-2@m">
          <div>
            <label className="uk-form-label" htmlFor="meetingDate">
              Дата совещания
            </label>

            <input
              className="uk-input"
              id="meetingDate"
              type="date"
              value={meetingDate}
              onChange={(event) => setMeetingDate(event.target.value)}
              required
            />
          </div>

          <div>
            <label className="uk-form-label" htmlFor="audio">
              Аудиозапись
            </label>

            <input
              className="uk-input"
              id="audio"
              type="file"
              accept="audio/*"
              onChange={(event) =>
                setAudioFile(event.target.files?.[0] ?? null)
              }
              required
            />
          </div>
        </div>

        <button
          className="uk-button uk-button-primary uk-margin-top"
          type="submit"
          disabled={isGenerating}
        >
          {isGenerating
            ? "Формируем отчёт..."
            : "Сформировать отчёт"}
        </button>
      </form>

      {report && (
        <article className="uk-card uk-card-default uk-card-body uk-margin-top">
          <h2>{report.topic}</h2>

          <p>
            <strong>Дата:</strong> {report.meeting_date}
          </p>

          <h3>Ключевые вопросы</h3>
          <ul>
            {report.key_questions.map((question, index) => (
              <li key={`${index}-${question}`}>{question}</li>
            ))}
          </ul>

          <h3>Краткое содержание</h3>
          <p>{report.summary}</p>

          <h3>Задачи</h3>
          <ul>
            {report.tasks.map((task, index) => (
              <li key={`${index}-${task.content}`}>
                {task.content} — до {task.deadline}
              </li>
            ))}
          </ul>
        </article>
      )}
    </section>
  );
}

export default HomePage;