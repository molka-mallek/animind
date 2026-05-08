import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Layout from './components/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Modules from './pages/Modules'
import DogEmotion from './modules/DogEmotion'
import EyeInfection from './modules/EyeInfection'
import ChickenFowlpox from './modules/ChickenFowlpox'
import BirdDroppings from './modules/BirdDroppings'
import SkinAnomaly from './modules/SkinAnomaly'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="modules" element={<Modules />} />
          <Route path="modules/dog-emotion" element={<DogEmotion />} />
          <Route path="modules/eye-infection" element={<EyeInfection />} />
          <Route path="modules/chicken-fowlpox" element={<ChickenFowlpox />} />
          <Route path="modules/bird-droppings" element={<BirdDroppings />} />
          <Route path="modules/skin-anomaly" element={<SkinAnomaly />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
