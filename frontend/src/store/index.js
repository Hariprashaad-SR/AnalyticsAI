import { configureStore } from '@reduxjs/toolkit'
import reportReducer from './reportSlice'

export const store = configureStore({
  reducer: {
    report: reportReducer,
  },
})
