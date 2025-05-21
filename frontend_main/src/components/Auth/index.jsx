import React, { useState } from "react";
import Input from "../Input";
import Button from "../Button";
import { useNavigate } from "react-router-dom";
import { login } from "../../services/authService";
import { setIsAuthenticated, setUser } from "../../state";
import { useDispatch } from "react-redux";

const Auth = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showError, setShowError] = useState(false);

  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (email && password) {
      try {
        const response = await login(email, password);
        console.log(response);
        dispatch(setIsAuthenticated(true));
        dispatch(setUser(response.user));
        navigate("/"); // Перенаправляем в профиль
      } catch (error) {
        alert(error.response?.data.detail);
        console.error("Ошибка авторизации: ", error);
      }
    } else {
      setShowError(true);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-white p-6 rounded-lg w-1/3 flex flex-col">
        <p className="font-semibold text-2xl mb-1 self-center">
          Вход в систему
        </p>
        <hr className="w-2/3 self-center border-brand-blue" />
        <div className="mt-3">
          <Input
            type="text"
            title="Логин"
            onChange={(e) => setEmail(e.target.value)}
            value={email}
            onKeyPress={handleKeyPress}
          />
          <Input
            type="password"
            title="Пароль"
            onChange={(e) => setPassword(e.target.value)}
            value={password}
            onKeyPress={handleKeyPress}
          />
          {showError && (
            <div className="text-red-600 text-xs">Вы заполнили не все поля</div>
          )}
        </div>
        <div className="self-center mt-7">
          <Button text="Войти" onClick={handleSubmit} />
        </div>
      </div>
    </div>
  );
};

export default Auth;
