import { useEffect, useState } from "react";

import { createEmployee } from "../../services/employeeService";
import {
  getDepartments,
  getPositions,
} from "../../services/directoryService";

const initialForm = {
  email: "",
  password: "",
  firstName: "",
  lastName: "",
  patronymic: "",
  departmentId: "",
  positionId: "",
};

function EmployeeForm({ onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);
  const [isLoadingDirectories, setIsLoadingDirectories] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
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

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setIsSaving(true);
    setError("");

    try {
      await createEmployee({
        email: form.email.trim(),
        password: form.password,
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        patronymic: form.patronymic.trim(),
        department_id: Number(form.departmentId),
        position_id: Number(form.positionId),
      });

      setForm(initialForm);
      onCreated();
    } catch (requestError) {
      const responseData = requestError.response?.data;

      if (responseData && typeof responseData === "object") {
        const firstMessage = Object.values(responseData).flat()[0];
        setError(String(firstMessage));
      } else {
        setError("Не удалось создать сотрудника.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form
      className="uk-card uk-card-default uk-card-body uk-margin-bottom"
      onSubmit={handleSubmit}
    >
      <h2 className="uk-card-title">Добавить сотрудника</h2>

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      <div
        className="uk-child-width-1-2@m uk-grid-small"
        data-uk-grid
      >
        <div>
          <label className="uk-form-label" htmlFor="lastName">
            Фамилия
          </label>
          <input
            className="uk-input"
            id="lastName"
            name="lastName"
            value={form.lastName}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="uk-form-label" htmlFor="firstName">
            Имя
          </label>
          <input
            className="uk-input"
            id="firstName"
            name="firstName"
            value={form.firstName}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="uk-form-label" htmlFor="patronymic">
            Отчество
          </label>
          <input
            className="uk-input"
            id="patronymic"
            name="patronymic"
            value={form.patronymic}
            onChange={handleChange}
          />
        </div>

        <div>
          <label className="uk-form-label" htmlFor="email">
            Email
          </label>
          <input
            className="uk-input"
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="uk-form-label" htmlFor="password">
            Пароль
          </label>
          <input
            className="uk-input"
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />
        </div>

        <div>
          <label className="uk-form-label" htmlFor="departmentId">
            Отдел
          </label>
          <select
            className="uk-select"
            id="departmentId"
            name="departmentId"
            value={form.departmentId}
            onChange={handleChange}
            disabled={isLoadingDirectories}
            required
          >
            <option value="">Выберите отдел</option>

            {departments.map((department) => (
              <option key={department.id} value={department.id}>
                {department.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="uk-form-label" htmlFor="positionId">
            Должность
          </label>
          <select
            className="uk-select"
            id="positionId"
            name="positionId"
            value={form.positionId}
            onChange={handleChange}
            disabled={isLoadingDirectories}
            required
          >
            <option value="">Выберите должность</option>

            {positions.map((position) => (
              <option key={position.id} value={position.id}>
                {position.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        className="uk-button uk-button-primary uk-margin-top"
        type="submit"
        disabled={isSaving || isLoadingDirectories}
      >
        {isSaving ? "Создаём..." : "Добавить сотрудника"}
      </button>
    </form>
  );
}

export default EmployeeForm;