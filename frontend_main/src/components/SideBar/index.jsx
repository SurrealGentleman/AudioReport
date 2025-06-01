import { useEffect, useState } from "react";
import { logoWhite } from "../../assets";
import { menu } from "../../constants/sidebar";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";

const SideBar = ({}) => {
  const isAdmin = useSelector((state) => state.global.user).is_admin;
  const navigate = useNavigate();
  const [hideTab, setHideTab] = useState([]);

  useEffect(() => {
    if (!isAdmin) {
      setHideTab([...hideTab, "admin"]);
    }
  }, [isAdmin]);

  return (
    <div className="fixed bottom-0 top-0 flex flex-col bg-brand-blue w-56 items-center">
      <img className="mt-3 mb-5" src={logoWhite} width={150} />
      <div className="space-y-2 w-full">
        {menu.map((item) => {
          return (
            <>
              {!hideTab?.includes(item.id) && (
                <div
                  key={item.id}
                  className={`mx-2 px-5 py-1 ${
                    window.location.pathname === item.link
                      ? "bg-brand-purple"
                      : "bg-[#EFEEEE]"
                  } rounded-lg cursor-pointer hover:bg-brand-purple`}
                  onClick={() => {
                    navigate(item.link);
                  }}
                >
                  {item.title}
                </div>
              )}
            </>
          );
        })}
      </div>
    </div>
  );
};

export default SideBar;
