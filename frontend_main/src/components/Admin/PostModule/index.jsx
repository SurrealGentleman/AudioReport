import React, { useEffect, useState } from "react";
import Input from "../../Input/index.jsx";
import Button from "../../Button/index.jsx";
import { postPosts } from "../../../services/postService.js";
import { post } from "../../../constants/tables.js";
import Table from "./Table/index.jsx";
import { getPosts } from "../../../services/postService.js";

const PostModule = () => {
  const [namePost, setNamePost] = useState();
  const [allPosts, setAllPosts] = useState();
  const [updatePosts, setUpdatePosts] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPosts();
        setAllPosts(data);
      } catch (error) {
        console.error("Ошибка при получении должностей:", error);
      }
    })();
  }, [updatePosts]);

  const handleAddPost = async (e) => {
    e.preventDefault();
    try {
      const data = await postPosts(namePost);
      setAllPosts(data);
    } catch (error) {
      console.error("Ошибка добавления должности: ", error);
    }
  };

  return (
    <div>
      <div className="bg-white p-6 rounded-lg space-y-5">
        <div className="w-2/3">
          <Input
            type="text"
            title="Наименование"
            onChange={(e) => setNamePost(e.target.value)}
          />
        </div>
        <Button
          text="Добавить должность"
          buttonStyle="text-sm"
          onClick={handleAddPost}
        />
      </div>
      <Table
        headers={post}
        items={allPosts}
        updatePosts={updatePosts}
        setUpdatePosts={setUpdatePosts}
      />
    </div>
  );
};

export default PostModule;
