import React, { useState, useEffect } from "react";
import Meeting from "../components/Meeting";
import { getMeetings } from "../services/meetingService";
import { useSelector } from "react-redux";

const MeetingsPage = () => {
  const user = useSelector((state) => state.global.user);
  const [allMeetings, setAllMeetings] = useState();

  useEffect(() => {
    (async () => {
      try {
        const data = await getMeetings(user.id);
        setAllMeetings(data);
      } catch (error) {
        console.error("Ошибка при получении отделов:", error);
      }
    })();
  }, []);

  return (
    <div className="w-2/3">
      <p className="text-3xl">Отчеты</p>
      <div className="space-y-8 mt-5">
        {!allMeetings && (
          <p className="text-gray-700">
            Сформированных отчетов с вашим участием нет
          </p>
        )}
        {allMeetings?.map((meeting) => {
          return <Meeting key={meeting.id} meeting={meeting} />;
        })}
      </div>
    </div>
  );
};

export default MeetingsPage;
