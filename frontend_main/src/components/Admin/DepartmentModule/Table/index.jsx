import React from "react";
import { trash } from "../../../../assets";
import { deleteDepartment } from "../../../../services/departmentService";

const Table = ({
  headers,
  items,
  updateDepartments,
  setUpdateDepartments,
  setChangeDepartment,
}) => {
  const handleDelete = async (departmentId) => {
    try {
      await deleteDepartment(departmentId);
      setUpdateDepartments(updateDepartments + 1);
    } catch (error) {
      console.error("Ошибка удаления отдела: ", error);
    }
  };

  return (
    <div className="my-7 bg-white rounded-lg">
      <div className="bg-brand-purple p-3 rounded-t-lg">
        {headers?.map((header) => (
          <div key={header.name} className="font-semibold">
            {header.name}
          </div>
        ))}
      </div>
      <div>
        {items?.map((item) => {
          return (
            <div
              className="flex justify-between hover:bg-brand-grey cursor-pointer"
              onClick={() => setChangeDepartment(item)}
            >
              <div className="py-4 px-3 border-r border-b w-full">
                {item.name}
              </div>
              <div className="p-4 border-b">
                <img
                  className="cursor-pointer"
                  src={trash}
                  width={20}
                  onClick={() => handleDelete(item.id)}
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
