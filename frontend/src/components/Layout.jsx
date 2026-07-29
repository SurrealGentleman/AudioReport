import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/useAuth";

function MenuLink({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        isActive ? "uk-text-primary uk-text-bold" : ""
      }
    >
      {children}
    </NavLink>
  );
}

function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <>
      <header className="uk-navbar-container">
        <div className="uk-container">
          <nav className="uk-navbar" aria-label="Основная навигация">
            <div className="uk-navbar-left">
              <NavLink className="uk-navbar-item uk-logo" to="/">
                AudioReport
              </NavLink>

              <ul className="uk-navbar-nav">
                <li>
                  <MenuLink to="/">Создать отчёт</MenuLink>
                </li>

                <li>
                  <MenuLink to="/meetings">Отчёты</MenuLink>
                </li>

                <li>
                  <MenuLink to="/tasks">Задачи</MenuLink>
                </li>

                {user?.is_staff && (
                  <li>
                    <MenuLink to="/admin">Администрирование</MenuLink>
                  </li>
                )}
              </ul>
            </div>

            <div className="uk-navbar-right">
              <span className="uk-navbar-item">
                {user?.last_name} {user?.first_name}
              </span>

              <div className="uk-navbar-item">
                <button
                  className="uk-button uk-button-default uk-button-small"
                  type="button"
                  onClick={handleLogout}
                >
                  Выйти
                </button>
              </div>
            </div>
          </nav>
        </div>
      </header>

      <main className="uk-section uk-section-small">
        <div className="uk-container">
          <Outlet />
        </div>
      </main>
    </>
  );
}

export default Layout;