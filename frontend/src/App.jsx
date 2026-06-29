import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './AppContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Hunt from './pages/Hunt';
import Identity from './pages/Identity';
import Media from './pages/Media';
import Velocity from './pages/Velocity';
import Network from './pages/Network';
import Bots from './pages/Bots';
import Tactics from './pages/Tactics';
import Infrastructure from './pages/Infrastructure';
import Evidence from './pages/Evidence';
import Geo from './pages/Geo';
import Reports from './pages/Reports';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/hunt" element={<Hunt />} />
            <Route path="/identity" element={<Identity />} />
            <Route path="/media" element={<Media />} />
            <Route path="/velocity" element={<Velocity />} />
            <Route path="/network" element={<Network />} />
            <Route path="/bots" element={<Bots />} />
            <Route path="/tactics" element={<Tactics />} />
            <Route path="/infrastructure" element={<Infrastructure />} />
            <Route path="/evidence" element={<Evidence />} />
            <Route path="/geo" element={<Geo />} />
            <Route path="/reports" element={<Reports />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
