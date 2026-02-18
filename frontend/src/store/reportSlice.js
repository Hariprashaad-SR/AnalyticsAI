import { createSlice } from '@reduxjs/toolkit'

const reportSlice = createSlice({
  name: 'report',
  initialState: {
    expandedReports: {},
  },
  reducers: {
    toggleReport: (state, action) => {
      const id = action.payload
      state.expandedReports[id] = !state.expandedReports[id]
    },
    setReport: (state, action) => {
      const { id, value } = action.payload
      state.expandedReports[id] = value
    },
  },
})

export const { toggleReport, setReport } = reportSlice.actions
export default reportSlice.reducer
