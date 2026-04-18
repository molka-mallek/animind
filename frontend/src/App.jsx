import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Layout from './components/Layout'

import Home from './pages/Home'

import Dashboard from './pages/Dashboard'

import Modules from './pages/Modules'

import DogEmotion from './modules/DogEmotion'

export default function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Layout />}>

          <Route index element={<Home />} />

          <Route path="dashboard" element={<Dashboard />} />

          <Route path="modules" element={<Modules />} />

          <Route path="modules/dog-emotion" element={<DogEmotion />} />

          <Route path="*" element={<Navigate to="/" replace />} />

        </Route>

      </Routes>

    </BrowserRouter>

  )

}