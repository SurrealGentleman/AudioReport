import { createSlice } from "@reduxjs/toolkit";

export const userSlice = createSlice({
  name: "global",
  initialState: {
    isAuthenticated: false,
    user: "",
  },
  reducers: {
    setIsAuthenticated: (state, action) => {
      state.isAuthenticated = action.payload;
    },
    setUser: (state, action) => {
      state.user = action.payload;
    },
  },
});

export const { setIsAuthenticated, setUser } = userSlice.actions;

export default userSlice.reducer;
