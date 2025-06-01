import { configureStore } from "@reduxjs/toolkit";
import userReducer from "./state";

export default configureStore({
  reducer: {
    global: userReducer,
  },
});
