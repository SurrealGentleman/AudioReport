import React from "react";
import { trash, admin } from "../../../../assets";
import { deleteEmployee } from "../../../../services/employeeService";

const Table = ({ headers, items, updateEmployees, setUpdateEmployees }) => {
  const handleDelete = async (employeeId) => {
    try {
      await deleteEmployee(employeeId);
      setUpdateEmployees(updateEmployees + 1);
    } catch (error) {
      console.error("Ошибка удаления сотрудника: ", error);
    }
  };

  return (
    <div className="my-7 bg-white rounded-lg">
      <div className="bg-brand-purple rounded-t-lg flex">
        {headers?.map((header) => (
          <div
            key={header.name}
            className="font-semibold w-1/4 py-3 flex justify-center border-r"
          >
            {header.name}
          </div>
        ))}
        <div className="w-14"></div>
        {/* колонка с иконкой для удаления */}
      </div>
      <div>
        {items?.map((item) => {
          const isAdmin = item.is_admin;
          const employeeId = item.id;

          delete item.first_name;
          delete item.last_name;
          delete item.patronymic;
          delete item.password;
          return (
            <div className="flex justify-between" key={item.email}>
              <div className="border-b w-full flex justify-between">
                {Object.entries(item).map(([key, value]) => (
                  <>
                    {key !== "is_admin" && key !== "id" && (
                      <div
                        key={key}
                        className={`flex py-4 px-3 border-r text-sm relative w-1/4 ${
                          key === "email" && "break-all"
                        }`}
                      >
                        {typeof value === "string" ? value : value?.name}
                        {key === "full_name" && item.is_admin && (
                          <img
                            className="absolute top-1 right-1"
                            src={admin}
                            width={15}
                            title="Администратор"
                          />
                        )}
                      </div>
                    )}
                  </>
                ))}
              </div>
              <div className="p-4 border-b flex items-center justify-center">
                <img
                  className="cursor-pointer"
                  src={trash}
                  width={20}
                  onClick={() => handleDelete(employeeId)}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Table;
