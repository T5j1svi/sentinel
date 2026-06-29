import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  // Hunt results — shared across all intelligence modules
  const [huntResults, setHuntResults] = useState(() => {
    const saved = localStorage.getItem('sentinel_huntResults');
    return saved ? JSON.parse(saved) : null;
  });
  const [huntNarrative, setHuntNarrative] = useState(() => {
    return localStorage.getItem('sentinel_huntNarrative') || '';
  });
  
  // Case management
  const [caseId, setCaseId] = useState('default');
  const [caseName, setCaseName] = useState('New Investigation');
  
  // Evidence tracking
  const [evidenceCount, setEvidenceCount] = useState(0);
  
  // Active async tasks
  const [activeTasks, setActiveTasks] = useState(0);
  
  // Threat level (derived from analysis)
  const [threatLevel, setThreatLevel] = useState('Minimal');

  // Store hunt results and make them available to all modules
  const storeHuntResults = useCallback((results, narrative) => {
    setHuntResults(results);
    localStorage.setItem('sentinel_huntResults', JSON.stringify(results));
    
    if (narrative) {
      setHuntNarrative(narrative);
      localStorage.setItem('sentinel_huntNarrative', narrative);
    }
  }, []);

  const [automatedData, setAutomatedDataState] = useState(() => {
    const saved = localStorage.getItem('sentinel_automatedData');
    return saved ? JSON.parse(saved) : {
      bots: null,
      geo: null,
      tactics: null,
      network: null,
      infrastructure: null,
    };
  });

  const setAutomatedData = useCallback((updater) => {
    setAutomatedDataState(prev => {
      const newData = typeof updater === 'function' ? updater(prev) : updater;
      localStorage.setItem('sentinel_automatedData', JSON.stringify(newData));
      return newData;
    });
  }, []);

  const incrementEvidence = useCallback(() => {
    setEvidenceCount(prev => prev + 1);
  }, []);

  const startTask = useCallback(() => {
    setActiveTasks(prev => prev + 1);
  }, []);

  const endTask = useCallback(() => {
    setActiveTasks(prev => Math.max(0, prev - 1));
  }, []);

  const value = {
    // Hunt data
    huntResults,
    huntNarrative,
    storeHuntResults,
    
    // Case
    caseId,
    setCaseId,
    caseName,
    setCaseName,
    
    // Evidence
    evidenceCount,
    setEvidenceCount,
    incrementEvidence,
    
    // Tasks
    activeTasks,
    startTask,
    endTask,
    
    // Threat
    threatLevel,
    setThreatLevel,
    
    // Automated pipeline data
    automatedData,
    setAutomatedData,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export default AppContext;
