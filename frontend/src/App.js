import React from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from "./components/Register";
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ForgotPassword from './components/ForgotPassword';
import ChangePassword from './components/ChangePassword';




function App() {
  return (
   <Router>
    <Routes>
      <Route path="/" element={<Login/>}/>
      <Route path="/dashboard" element={<Dashboard/>}/>
      <Route path="/register" element={<Register/>}/>
      <Route path="/changepassword" element={<ChangePassword/>}/>
      <Route path="/forgotpassword" element={<ForgotPassword/>}/>
    </Routes>
  </Router>
   
  );
}

export default App;
