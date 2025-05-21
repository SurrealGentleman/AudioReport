import Button from "../Button";
import { logout } from "../../services/authService";
import { useDispatch, useSelector } from "react-redux";
import { setIsAuthenticated } from "../../state";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const user = useSelector((state) => state.global.user);

  const userLogout = async (e) => {
    e.preventDefault();
    try {
      await logout();
      dispatch(setIsAuthenticated(false));
      navigate("/login"); // Перенаправляем в профиль
    } catch (error) {
      console.error("Ошибка выхода: ", error);
    }
  };

  return (
    <div className="h-12 bg-brand-purple flex justify-end items-center">
      <p className=" font-semibold mr-3">
        {user?.last_name} {user?.first_name}
      </p>
      <Button text="Выйти" onClick={userLogout} buttonStyle="mr-3" />
    </div>
  );
};

export default Header;
