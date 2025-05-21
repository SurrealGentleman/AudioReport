import Auth from "../components/Auth";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

const AuthPage = () => {
  const isAuthenticated = useSelector((state) => state.global.isAuthenticated);
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = Cookies.get("access_token");
    if (accessToken) {
      navigate("/");
    }
  }, [isAuthenticated]);

  return <Auth />;
};

export default AuthPage;
