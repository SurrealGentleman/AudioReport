import { useEffect, useState } from "react";

function DirectoryManager({
  title,
  itemName,
  loadItems,
  createItem,
  deleteItem,
}) {
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignoreResult = false;

    async function load() {
      setIsLoading(true);
      setError("");

      try {
        const data = await loadItems();

        if (!ignoreResult) {
          setItems(data);
        }
      } catch {
        if (!ignoreResult) {
          setError(`Не удалось загрузить: ${title.toLowerCase()}.`);
        }
      } finally {
        if (!ignoreResult) {
          setIsLoading(false);
        }
      }
    }

    load();

    return () => {
      ignoreResult = true;
    };
  }, [loadItems, title]);

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedName = name.trim();

    if (!trimmedName) {
      return;
    }

    setIsSaving(true);
    setError("");

    try {
      const createdItem = await createItem(trimmedName);
      setItems((currentItems) => [...currentItems, createdItem]);
      setName("");
    } catch {
      setError(`Не удалось добавить: ${itemName.toLowerCase()}.`);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(item) {
    const confirmed = window.confirm(
      `Удалить «${item.name}»?`
    );

    if (!confirmed) {
      return;
    }

    setError("");

    try {
      await deleteItem(item.id);

      setItems((currentItems) =>
        currentItems.filter(
          (currentItem) => currentItem.id !== item.id
        )
      );
    } catch {
      setError(
        `Не удалось удалить «${item.name}». Возможно, запись используется.`
      );
    }
  }

  return (
    <section className="uk-card uk-card-default uk-card-body">
      <h2 className="uk-card-title">{title}</h2>

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      <form
        className="uk-grid-small"
        data-uk-grid
        onSubmit={handleSubmit}
      >
        <div className="uk-width-expand">
          <input
            className="uk-input"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder={`Название: ${itemName.toLowerCase()}`}
            required
          />
        </div>

        <div className="uk-width-auto">
          <button
            className="uk-button uk-button-primary"
            type="submit"
            disabled={isSaving}
          >
            {isSaving ? "Добавляем..." : "Добавить"}
          </button>
        </div>
      </form>

      {isLoading ? (
        <p>Загрузка...</p>
      ) : items.length === 0 ? (
        <p className="uk-text-muted">Список пока пуст.</p>
      ) : (
        <table className="uk-table uk-table-divider uk-table-middle">
          <thead>
            <tr>
              <th>Название</th>
              <th className="uk-table-shrink">Действия</th>
            </tr>
          </thead>

          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>
                  <button
                    className="uk-button uk-button-danger uk-button-small"
                    type="button"
                    onClick={() => handleDelete(item)}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default DirectoryManager;