import { useEffect, useState } from "react";
import EmployeeForm from "./EmployeeForm";

import {
  getEmployees,
  updateEmployeeAccess,
} from "../../services/employeeService";

function EmployeeManager() {
  const [employees, setEmployees] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingEmployeeId, setUpdatingEmployeeId] = useState(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignoreResult = false;

    async function loadEmployees() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getEmployees();

        if (!ignoreResult) {
          setEmployees(data);
        }
      } catch {
        if (!ignoreResult) {
          setError("Не удалось загрузить сотрудников.");
        }
      } finally {
        if (!ignoreResult) {
          setIsLoading(false);
        }
      }
    }

    loadEmployees();

    return () => {
      ignoreResult = true;
    };
  }, [reloadKey]);

  async function handleActiveChange(employee) {
    setUpdatingEmployeeId(employee.id);
    setError("");

    try {
      const updatedAccess = await updateEmployeeAccess(employee.id, {
        is_active: !employee.is_active,
      });

      setEmployees((currentEmployees) =>
        currentEmployees.map((currentEmployee) =>
          currentEmployee.id === employee.id
            ? { ...currentEmployee, ...updatedAccess }
            : currentEmployee
        )
      );
    } catch {
      setError("Не удалось изменить доступ сотрудника.");
    } finally {
      setUpdatingEmployeeId(null);
    }
  }

  if (isLoading) {
    return <p>Загружаем сотрудников...</p>;
  }

  return (
    <section className="uk-card uk-card-default uk-card-body">
      <h2 className="uk-card-title">Сотрудники</h2>

      <EmployeeForm
        onCreated={() => {
          setReloadKey((currentKey) => currentKey + 1);
        }}
      />

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      {employees.length === 0 ? (
        <p className="uk-text-muted">Сотрудников пока нет.</p>
      ) : (
        <div className="uk-overflow-auto">
          <table className="uk-table uk-table-divider uk-table-middle">
            <thead>
              <tr>
                <th>Сотрудник</th>
                <th>Email</th>
                <th>Отдел</th>
                <th>Должность</th>
                <th>Роль</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>

            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id}>
                  <td>{employee.full_name}</td>
                  <td>{employee.email}</td>
                  <td>{employee.department?.name ?? "Не указан"}</td>
                  <td>{employee.position?.name ?? "Не указана"}</td>
                  <td>
                    {employee.is_staff
                      ? "Администратор"
                      : "Сотрудник"}
                  </td>
                  <td>
                    <span
                      className={
                        employee.is_active
                          ? "uk-label uk-label-success"
                          : "uk-label"
                      }
                    >
                      {employee.is_active ? "Активен" : "Отключён"}
                    </span>
                  </td>
                  <td>
                    <button
                      className={
                        employee.is_active
                          ? "uk-button uk-button-danger uk-button-small"
                          : "uk-button uk-button-primary uk-button-small"
                      }
                      type="button"
                      disabled={updatingEmployeeId === employee.id}
                      onClick={() => handleActiveChange(employee)}
                    >
                      {updatingEmployeeId === employee.id
                        ? "Сохраняем..."
                        : employee.is_active
                          ? "Отключить"
                          : "Включить"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default EmployeeManager;