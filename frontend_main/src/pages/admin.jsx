import React, { useState } from "react";
import { adminMenu } from "../constants/adminMenu";
import PostModule from "../components/Admin/PostModule";
import DepartmentModule from "../components/Admin/DepartmentModule";
import EmployeeModule from "../components/Admin/EmployeeModule";

const AdminPage = () => {
  const [currentBlock, setCurrentBlock] = useState("employee");

  return (
    <div className="w-2/3">
      <p className="text-3xl">Управление данными</p>
      <div className="flex gap-5 mt-5">
        {adminMenu.map((block) => {
          return (
            <div
              key={block.id}
              className={`${
                currentBlock === block.id
                  ? "bg-brand-blue text-white"
                  : "bg-brand-purple text-black"
              }  py-1.5 px-7 rounded-lg cursor-pointer`}
              onClick={() => setCurrentBlock(block.id)}
            >
              {block.title}
            </div>
          );
        })}
      </div>
      <div className="mt-5">
        {currentBlock === "post" && <PostModule />}
        {currentBlock === "department" && <DepartmentModule />}
        {currentBlock === "employee" && <EmployeeModule />}
      </div>
    </div>
  );
};

export default AdminPage;
