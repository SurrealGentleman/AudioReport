import "@fontsource/m-plus-rounded-1c"; // Defaults to weight 400

import React, { useState, useEffect } from "react";
import "./App.css";
import { Routes, useNavigate } from "react-router-dom";
import { Route } from "react-router-dom";
import HomePage from "./pages/home";
import AuthPage from "./pages/auth";
import TasksPage from "./pages/tasks";
import SideBar from "./components/SideBar";
import Header from "./components/Header";
import MeetingsPage from "./pages/meetings";
import { useDispatch, useSelector } from "react-redux";
import Cookies from "js-cookie";
import { setIsAuthenticated } from "./state";
import AdminPage from "./pages/admin";

function App() {
  const isAuthenticated = useSelector((state) => state.global.isAuthenticated);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = Cookies.get("access_token");
    if (accessToken) {
      dispatch(setIsAuthenticated(true));
    } else {
      dispatch(setIsAuthenticated(false));
      navigate("/login");
    }
  }, [dispatch]);

  return (
    <div className="App">
      {isAuthenticated && <SideBar />}
      {isAuthenticated && <Header />}
      <div className={`${isAuthenticated && "main"}`}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/meetings" element={<MeetingsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
