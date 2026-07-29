import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

function AuthPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setIsLoading(true);

    try {
      
      await login(email, password);
      navigate("/");

    } catch (requestError) {
      const message =
        requestError.response?.data?.detail ??
        "Не удалось выполнить вход. Проверьте данные и доступность сервера.";

      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main
      className="uk-flex uk-flex-center uk-flex-middle uk-padding"
      style={{ minHeight: "100vh" }}
    >
      <div className="uk-card uk-card-default uk-card-body uk-width-medium">
        <h1 className="uk-card-title uk-text-center">Вход в систему</h1>

        {error && (
          <div className="uk-alert-danger uk-padding-small">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="uk-margin">
            <label className="uk-form-label" htmlFor="email">
              Электронная почта
            </label>

            <div className="uk-form-controls">
              <input
                className="uk-input"
                id="email"
                name="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="uk-margin">
            <label className="uk-form-label" htmlFor="password">
              Пароль
            </label>

            <div className="uk-form-controls">
              <input
                className="uk-input"
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
          </div>

          <button
            className="uk-button uk-button-primary uk-width-1-1"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? "Выполняется вход..." : "Войти"}
          </button>
        </form>
      </div>
    </main>
  );
}

export default AuthPage;