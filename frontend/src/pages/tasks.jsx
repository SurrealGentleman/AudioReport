import { useEffect, useState } from "react";

import { useAuth } from "../auth/useAuth";
import { getTasks, patchTask } from "../services/taskService";

function TasksPage() {
  const { user } = useAuth();

  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingTaskId, setUpdatingTaskId] = useState(null);

  const userId = user?.id;

  useEffect(() => {
    if (!userId) {
      setIsLoading(false);
      return;
    }

    let ignoreResult = false;

    async function loadTasks() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getTasks();

        if (!ignoreResult) {
          setTasks(data);
        }
      } catch {
        if (!ignoreResult) {
          setError("Не удалось загрузить задачи.");
        }
      } finally {
        if (!ignoreResult) {
          setIsLoading(false);
        }
      }
    }

    loadTasks();

    return () => {
      ignoreResult = true;
    };
  }, [userId]);

  async function handleStatusChange(task) {
    setUpdatingTaskId(task.id);
    setError("");

    try {
      const newStatus = !task.status;

      await patchTask(task.id, newStatus);

      setTasks((currentTasks) =>
        currentTasks.map((currentTask) =>
          currentTask.id === task.id
            ? { ...currentTask, status: newStatus }
            : currentTask
        )
      );
    } catch {
      setError("Не удалось изменить статус задачи.");
    } finally {
      setUpdatingTaskId(null);
    }
  }

  if (isLoading) {
    return (
      <div className="uk-text-center uk-padding">
        <div data-uk-spinner />
        <p>Загружаем задачи...</p>
      </div>
    );
  }

  return (
    <section>
      <h1>Задачи</h1>

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="uk-card uk-card-default uk-card-body">
          У вас пока нет задач.
        </div>
      ) : (
        <div className="uk-grid-small" data-uk-grid>
          {tasks.map((task) => (
            <article className="uk-width-1-1" key={task.id}>
              <div className="uk-card uk-card-default uk-card-body">
                <div className="uk-flex uk-flex-between uk-flex-middle">
                  <h2 className="uk-card-title uk-margin-remove">
                    Задача №{task.id}
                  </h2>

                  <span
                    className={
                      task.status
                        ? "uk-label uk-label-success"
                        : "uk-label uk-label-warning"
                    }
                  >
                    {task.status ? "Выполнена" : "В процессе"}
                  </span>
                </div>

                <p>{task.content}</p>

                <dl className="uk-description-list">
                  <dt>Исполнитель</dt>
                  <dd>{user?.full_name ?? "Не указан"}</dd>

                  <dt>Дата назначения</dt>
                  <dd>{task.assigned_date ?? "Не указана"}</dd>

                  <dt>Срок выполнения</dt>
                  <dd>{task.due_date ?? "Не указан"}</dd>
                </dl>

                <button
                  className="uk-button uk-button-primary"
                  type="button"
                  onClick={() => handleStatusChange(task)}
                  disabled={updatingTaskId === task.id}
                >
                  {updatingTaskId === task.id
                    ? "Сохраняем..."
                    : task.status
                      ? "Вернуть в работу"
                      : "Отметить выполненной"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default TasksPage;