import { useState } from "react";
import { logoWhite } from "../../assets";
import { menu } from "../../constants/sidebar";
import { useNavigate } from "react-router-dom";

const SideBar = ({}) => {
  const navigate = useNavigate();

  return (
    <div className="fixed bottom-0 top-0 flex flex-col bg-brand-blue w-56 items-center">
      <img className="mt-3 mb-5" src={logoWhite} width={150} />
      <div className="space-y-2">
        {menu.map((item) => {
          return (
            <div
              key={item.id}
              className={`mx-2 px-5 py-1 ${
                window.location.pathname === item.link
                  ? "bg-brand-purple"
                  : "bg-[#EFEEEE]"
              } rounded-lg cursor-pointer hover:bg-brand-purple`}
              onClick={() => {
                // dispatch(setCurrentTab(item.id));
                navigate(item.link);
              }}
            >
              {item.title}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SideBar;
