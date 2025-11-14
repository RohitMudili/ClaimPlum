import { formatCurrency } from '../utils/helpers';
import briefcaseIcon from '../assets/briefcase-icon.webp';
import confirmIcon from '../assets/confirm-icon.webp';

const SalesConversion = ({ salesData, onReset }) => {
  const { sales_pitch, claim_preview, example_savings, contact_info } = salesData;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Hero - Compact */}
        <div className="p-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <img src={briefcaseIcon} alt="Business" className="w-12 h-12" />
          </div>

          <h1 className="text-3xl font-bold mb-2 text-gray-900">
            {sales_pitch?.headline || 'Join Plum Today!'}
          </h1>
          <p className="text-lg text-gray-600 mb-4">{salesData.message}</p>
          <p className="text-base text-gray-700 mb-6">
            {sales_pitch?.value_proposition}
          </p>

          {/* Quick Savings Example */}
          {!claim_preview && example_savings && (
            <div className="grid grid-cols-3 gap-3 max-w-xl mx-auto mb-6">
              <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="text-xs text-gray-600 mb-1">Without</div>
                <div className="text-xl font-bold text-red-600">₹1,500</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="text-xs text-gray-600 mb-1">With Plum</div>
                <div className="text-xl font-bold text-green-600">₹150</div>
              </div>
              <div className="p-3 bg-primary-50 rounded-lg border-2 border-primary-500">
                <div className="text-xs text-gray-600 mb-1">You Save</div>
                <div className="text-xl font-bold text-primary-600">90%</div>
              </div>
            </div>
          )}

          {/* Claim Preview for old format */}
          {claim_preview && (
            <div className="mb-6">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">Claimed</div>
                  <div className="text-xl font-bold text-gray-900">
                    {formatCurrency(claim_preview.your_claim_amount)}
                  </div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border-2 border-green-500">
                  <div className="text-xs text-green-700 mb-1">Plum Covers</div>
                  <div className="text-xl font-bold text-green-600">
                    {formatCurrency(claim_preview.plum_would_cover)}
                  </div>
                  <div className="text-xs text-green-600 mt-1">
                    {claim_preview.coverage_percentage}%
                  </div>
                </div>
                <div className="p-4 bg-primary-50 rounded-lg border-2 border-primary-500">
                  <div className="text-xs text-primary-700 mb-1">You Save</div>
                  <div className="text-xl font-bold text-primary-600">
                    {formatCurrency(claim_preview.your_savings)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Key Benefits - Top 4 only */}
          {sales_pitch?.key_benefits && (
            <div className="mb-6 space-y-2 text-left max-w-xl mx-auto">
              {sales_pitch.key_benefits.slice(0, 4).map((benefit, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <img src={confirmIcon} alt="Check" className="w-4 h-4 mt-1 flex-shrink-0" />
                  <p className="text-sm text-gray-700">{benefit}</p>
                </div>
              ))}
            </div>
          )}

          {/* Lead Captured */}
          {(salesData.lead_captured || salesData.lead_info?.captured) && (
            <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-r-lg">
              <div className="flex items-center justify-center">
                <img src={confirmIcon} alt="Success" className="w-4 h-4 mr-2" />
                <p className="text-sm text-green-800 font-medium">
                  Thanks! Our team will reach out soon!
                </p>
              </div>
            </div>
          )}

          {/* CTA Buttons - Prominent */}
          <div className="flex flex-col gap-3">
            <a
              href={sales_pitch?.cta_url || 'https://plumhq.com/get-quote'}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full px-8 py-4 bg-primary-600 text-white text-lg rounded-full font-bold hover:bg-primary-700 transition-colors shadow-lg hover:shadow-xl"
            >
              {sales_pitch?.cta || 'Get Free Quote'} →
            </a>

            <button
              onClick={onReset}
              className="w-full px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-full font-medium hover:bg-gray-50 transition-colors"
            >
              ← Back to Claims
            </button>
          </div>

          {/* Contact - Minimal */}
          {contact_info && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">Need help?</p>
              <div className="flex flex-wrap justify-center gap-2 text-xs">
                {contact_info.phone && (
                  <a href={`tel:${contact_info.phone}`} className="text-primary-600 hover:underline">
                    {contact_info.phone}
                  </a>
                )}
                {contact_info.email && (
                  <>
                    <span className="text-gray-400">•</span>
                    <a href={`mailto:${contact_info.email}`} className="text-primary-600 hover:underline">
                      {contact_info.email}
                    </a>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SalesConversion;
