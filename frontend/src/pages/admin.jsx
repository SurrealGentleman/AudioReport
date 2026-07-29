import { useState } from "react";

import { useAuth } from "../auth/useAuth";
import DirectoryManager from "../components/Admin/DirectoryManager";
import EmployeeManager from "../components/Admin/EmployeeManager";
import {
  createDepartment,
  createPosition,
  deleteDepartment,
  deletePosition,
  getDepartments,
  getPositions,
} from "../services/directoryService";

function AdminPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("employees");

  if (!user?.is_staff) {
    return (
      <div className="uk-alert-danger uk-padding">
        У вас нет доступа к администрированию.
      </div>
    );
  }

  return (
    <section>
      <h1>Администрирование</h1>

      <div className="uk-margin">
        <button
          className={
            activeTab === "employees"
              ? "uk-button uk-button-primary"
              : "uk-button uk-button-default"
          }
          type="button"
          onClick={() => setActiveTab("employees")}
        >
          Сотрудники
        </button>

        <button
          className={
            activeTab === "departments"
              ? "uk-button uk-button-primary"
              : "uk-button uk-button-default"
          }
          type="button"
          onClick={() => setActiveTab("departments")}
        >
          Отделы
        </button>

        <button
          className={
            activeTab === "positions"
              ? "uk-button uk-button-primary"
              : "uk-button uk-button-default"
          }
          type="button"
          onClick={() => setActiveTab("positions")}
        >
          Должности
        </button>
      </div>

      {activeTab === "employees" && <EmployeeManager />}

      {activeTab === "departments" && (
        <DirectoryManager
          title="Отделы"
          itemName="Отдел"
          loadItems={getDepartments}
          createItem={createDepartment}
          deleteItem={deleteDepartment}
        />
      )}

      {activeTab === "positions" && (
        <DirectoryManager
          title="Должности"
          itemName="Должность"
          loadItems={getPositions}
          createItem={createPosition}
          deleteItem={deletePosition}
        />
      )}
    </section>
  );
}

export default AdminPage;
