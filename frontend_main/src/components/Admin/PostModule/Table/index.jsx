import React from "react";
import { trash } from "../../../../assets";
import { deletePost } from "../../../../services/postService";

const Table = ({
  headers,
  items,
  updatePosts,
  setUpdatePosts,
  setChangePost,
}) => {
  const handleDelete = async (postId) => {
    try {
      await deletePost(postId);
      setUpdatePosts(updatePosts + 1);
    } catch (error) {
      console.error("Ошибка удаления должности: ", error);
    }
  };

  return (
    <div className="mt-7 bg-white rounded-lg">
      <div className="bg-brand-purple p-3 rounded-t-lg">
        {headers?.map((header) => (
          <div key={header.name} className="font-semibold">
            {header.name}
          </div>
        ))}
      </div>
      <div>
        {items?.map((item) => {
          return (
            <div
              className="flex justify-between hover:bg-brand-grey cursor-pointer"
              onClick={() => setChangePost(item)}
            >
              <div className="py-4 px-3 border-r border-b w-full">
                {item.name}
              </div>
              <div className="p-4 border-b">
                <img
                  className="cursor-pointer"
                  src={trash}
                  width={20}
                  onClick={() => handleDelete(item.id)}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Table;
