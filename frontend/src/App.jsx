import { useState, useEffect } from 'react';
import ClaimUpload from './components/ClaimUpload';
import DecisionDisplay from './components/DecisionDisplay';
import SalesConversion from './components/SalesConversion';
import healthIcon from './assets/health-insurance-icon.webp';

function App() {
  const [currentView, setCurrentView] = useState('upload'); // 'upload', 'decision', 'sales'
  const [claimData, setClaimData] = useState(null);

  // Scroll to top whenever view changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentView]);

  const handleClaimSuccess = (data, type) => {
    setClaimData(data);
    if (type === 'NOT_A_MEMBER') {
      setCurrentView('sales');
    } else if (type === 'REJECTED') {
      setCurrentView('decision'); // Show rejection in decision view
    } else {
      setCurrentView('decision');
    }
  };

  const handleReset = () => {
    setCurrentView('upload');
    setClaimData(null);
  };

  return (
    <div className="min-h-screen bg-[#f8f9fb]">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img src={healthIcon} alt="Health Insurance Logo" className="h-11 w-11 object-contain" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Plum OPD Claims</h1>
              </div>
            </div>
            {currentView !== 'upload' && (
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-primary-600 text-white rounded-full hover:bg-primary-800 transition-colors"
              >
                New Claim
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {currentView === 'upload' && (
          <ClaimUpload onSuccess={handleClaimSuccess} />
        )}

        {currentView === 'decision' && claimData && (
          <DecisionDisplay
            decision={claimData}
            claimId={claimData.claim_id}
            onReset={handleReset}
          />
        )}

        {currentView === 'sales' && claimData && (
          <SalesConversion salesData={claimData} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="text-sm text-gray-600">
              © 2025 Plum. Powered by AI. Built with ❤
            </div>
            <div className="flex space-x-6 text-sm">
              <a href="#" className="text-gray-600 hover:text-plum-600 transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="text-gray-600 hover:text-plum-600 transition-colors">
                Terms of Service
              </a>
              <a href="#" className="text-gray-600 hover:text-plum-600 transition-colors">
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;