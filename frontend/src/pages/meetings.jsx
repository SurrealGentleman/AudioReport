import { useEffect, useState } from "react";

import { getMeetings } from "../services/meetingService";

function MeetingsPage() {
  const [meetings, setMeetings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignoreResult = false;

    async function loadMeetings() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getMeetings();

        if (!ignoreResult) {
          setMeetings(data);
        }
      } catch {
        if (!ignoreResult) {
          setError("Не удалось загрузить отчёты.");
        }
      } finally {
        if (!ignoreResult) {
          setIsLoading(false);
        }
      }
    }

    loadMeetings();

    return () => {
      ignoreResult = true;
    };
  }, []);

  if (isLoading) {
    return <p className="uk-text-center">Загружаем отчёты...</p>;
  }

  return (
    <section>
      <h1>Отчёты</h1>

      {error && (
        <div className="uk-alert-danger uk-padding-small">
          {error}
        </div>
      )}

      {meetings.length === 0 ? (
        <div className="uk-card uk-card-default uk-card-body">
          Сохранённых отчётов пока нет.
        </div>
      ) : (
        <div className="uk-child-width-1-1 uk-grid-small" data-uk-grid>
          {meetings.map((meeting) => (
            <article key={meeting.id}>
              <div className="uk-card uk-card-default uk-card-body">
                <div className="uk-flex uk-flex-between uk-flex-wrap">
                  <h2 className="uk-card-title">
                    {meeting.topic}
                  </h2>

                  <span className="uk-label">
                    {meeting.meeting_date ?? "Дата не указана"}
                  </span>
                </div>

                <dl className="uk-description-list">
                  <dt>Дата создания отчёта</dt>
                  <dd>{meeting.report_date}</dd>

                  <dt>Участников</dt>
                  <dd>{meeting.participants?.length ?? 0}</dd>
                </dl>

                <div className="uk-flex uk-flex-wrap uk-grid-small" data-uk-grid>
                  {meeting.audio_path && (
                    <div>
                      <a
                        className="uk-button uk-button-default"
                        href={meeting.audio_path}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Открыть аудиозапись
                      </a>
                    </div>
                  )}

                  {meeting.report_path && (
                    <div>
                      <a
                        className="uk-button uk-button-primary"
                        href={meeting.report_path}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Открыть отчёт
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default MeetingsPage;