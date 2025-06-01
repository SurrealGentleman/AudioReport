import React from "react";
import { Link } from "react-router-dom";

const Meeting = ({ meeting }) => {
  return (
    <div className="bg-white p-6 rounded-lg space-y-10">
      <div className="text-xl font-semibold">"{meeting.topic}"</div>
      <div className="flex flex-col w-2/5 gap-3 justify-center">
        <div className="flex justify-between">
          <div>Дата формирования: </div>
          <div className="text-white bg-brand-blue px-2 py-1 text-sm rounded-lg">
            {meeting.report_date}
          </div>
        </div>
        <div className="flex justify-between items-center">
          <div>Дата проведения совещания: </div>
          <div className="text-white bg-brand-blue px-2 py-1 text-sm rounded-lg">
            {meeting.meeting_date}
          </div>
        </div>
      </div>
      <div className="flex gap-10">
        {meeting.audio_path && (
          <Link
            download
            to={meeting.audio_path}
            className="text-blue-700 underline underline-offset-4 cursor-pointer"
          >
            Скачать аудиозапись
          </Link>
        )}
        {meeting.report_path && (
          <Link
            download
            to={meeting.report_path}
            className="text-blue-700 underline underline-offset-4 cursor-pointer"
          >
            Скачать отчет
          </Link>
        )}
      </div>
    </div>
  );
};

export default Meeting;
