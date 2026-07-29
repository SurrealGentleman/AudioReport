import "@fontsource/m-plus-rounded-1c";
import "./App.css";

import { Route, Routes } from "react-router-dom";

import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./components/Layout";
import AdminPage from "./pages/admin";
import AuthPage from "./pages/auth";
import HomePage from "./pages/home";
import MeetingsPage from "./pages/meetings";
import TasksPage from "./pages/tasks";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/meetings" element={<MeetingsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;