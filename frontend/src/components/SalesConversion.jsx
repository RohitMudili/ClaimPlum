import { formatCurrency } from '../utils/helpers';
  import briefcaseIcon from '../assets/briefcase-icon.webp';
  import confirmIcon from '../assets/confirm-icon.webp';

  const SalesConversion = ({ salesData, onReset }) => {
    const { sales_pitch, claim_preview, policy_benefits, next_steps, contact_info } = salesData;

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Hero + Value Proposition + CTA - Single Unified Section */}
          <div className="p-8 border-b border-gray-200">
            <div className="flex items-center justify-center mb-6">
              <img src={briefcaseIcon} alt="Business" className="w-16 h-16" />
            </div>

            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold mb-3 text-gray-900">{sales_pitch?.headline || 'Join Plum Today!'}</h1>
              <p className="text-xl text-gray-600 mb-8">{salesData.message}</p>
            </div>

            <div className="max-w-3xl mx-auto">
              <div className="p-6 bg-primary-50 border-l-4 border-primary-500 rounded-r-lg mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">
                  Here's What You Would Have Saved
                </h2>
                <p className="text-base text-gray-800 font-medium">
                  {sales_pitch?.value_proposition}
                </p>
              </div>

              {sales_pitch?.urgency && (
                <div className="text-center">
                  <p className="text-gray-600 text-lg">{sales_pitch?.urgency}</p>
                </div>
              )}
            </div>
          </div>

          {/* Claim Analysis */}
          {claim_preview && (
            <div className="p-8 border-b border-gray-200">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
                We Analyzed Your Claim
              </h3>

              {/* Amount Breakdown */}
              <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-gray-200">
                  <div className="text-sm text-gray-600 mb-2">Your Claim Amount</div>
                  <div className="text-3xl font-bold text-gray-900">
                    {formatCurrency(claim_preview.your_claim_amount)}
                  </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-green-500">
                  <div className="text-sm text-green-700 mb-2">Plum Would Cover</div>
                  <div className="text-3xl font-bold text-green-600">
                    {formatCurrency(claim_preview.plum_would_cover)}
                  </div>
                  <div className="text-sm text-green-600 mt-1">
                    {claim_preview.coverage_percentage}% coverage
                  </div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border-2 border-primary-500">
                  <div className="text-sm text-primary-700 mb-2">Your Savings</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {formatCurrency(claim_preview.your_savings)}
                  </div>
                </div>
              </div>

              {/* What We Found & How It Works - Merged */}
              {(claim_preview.what_we_found || claim_preview.copay_details) && (
                <div className="p-5 bg-primary-50 border-l-4 border-primary-500 rounded-r-lg">
                  {/* What We Found */}
                  {claim_preview.what_we_found && (
                    <div className="mb-4">
                      <h4 className="font-semibold text-gray-900 mb-3">What We Found in Your Documents:</h4>
                      <div className="space-y-2 text-sm">
                        {claim_preview.what_we_found.diagnosis && (
                          <div>
                            <span className="text-gray-600">Diagnosis:</span>
                            <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.diagnosis}</span>
                          </div>
                        )}
                        {claim_preview.what_we_found.doctor && (
                          <div>
                            <span className="text-gray-600">Doctor:</span>
                            <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.doctor}</span>
                          </div>
                        )}
                        {claim_preview.what_we_found.hospital && (
                          <div>
                            <span className="text-gray-600">Hospital:</span>
                            <span className="ml-2 text-gray-900 font-medium">{claim_preview.what_we_found.hospital}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Copay Details */}
                  {claim_preview.copay_details && (
                    <div className={claim_preview.what_we_found ? 'pt-4 border-t border-primary-200' : ''}>
                      <h4 className="font-semibold text-gray-900 mb-2">How It Works:</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex items-center space-x-2">
                          <img src={confirmIcon} alt="Checkmark" className="w-4 h-4" />
                          <span className="text-gray-700">{claim_preview.copay_details.consultation}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <img src={confirmIcon} alt="Checkmark" className="w-4 h-4" />
                          <span className="text-gray-700">{claim_preview.copay_details.network_discount}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Policy Benefits */}
          {policy_benefits && (
            <div className="p-8">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
                Why Companies Choose Plum
              </h3>
              <div className="p-5 bg-green-50 border-l-4 border-green-500 rounded-r-lg">
                <div className="space-y-3">
                  {Object.entries(policy_benefits).map(([key, value]) => (
                    <div key={key} className="flex items-start space-x-3">
                      <img src={confirmIcon} alt="Benefit" className="w-5 h-5 mt-0.5 flex-shrink-0" />
                      <div>
                        <div className="font-semibold text-gray-900 capitalize">
                          {key.replace(/_/g, ' ')}
                        </div>
                        <div className="text-sm text-gray-700">{value}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Get Started - Unified Bottom Section */}
          <div className="p-8">
            {/* Lead Captured Confirmation */}
            {salesData.lead_captured && (
              <div className="mb-6 p-5 bg-green-50 border-l-4 border-green-500 rounded-r-lg">
                <div className="flex items-start">
                  <img src={confirmIcon} alt="Success" className="w-5 h-5 mr-3 mt-0.5" />
                  <p className="text-sm text-green-800 font-medium">
                    Thanks! We've captured your information. Our team will reach out soon!
                  </p>
                </div>
              </div>
            )}

            {/* Next Steps - Redesigned */}
            {next_steps && next_steps.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">How to Get Started</h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  {next_steps.map((step, index) => (
                    <div key={index} className="p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-400 transition-colors">
                      <div className="flex items-start space-x-3">
                        <span className="flex-shrink-0 w-7 h-7 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-xs">
                          {index + 1}
                        </span>
                        <p className="text-sm text-gray-700 leading-relaxed pt-0.5">{step}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Contact Info - Redesigned */}
            {contact_info && (
              <div className="mb-8">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Need Help? Contact Us</h4>
                <div className="flex flex-wrap gap-3">
                  {contact_info.email && (
                    <a
                      href={`mailto:${contact_info.email}`}
                      className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:border-primary-500 hover:text-primary-600 transition-colors"
                    >
                      {contact_info.email}
                    </a>
                  )}
                  {contact_info.phone && (
                    <a
                      href={`tel:${contact_info.phone}`}
                      className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:border-primary-500 hover:text-primary-600 transition-colors"
                    >
                      {contact_info.phone}
                    </a>
                  )}
                  {contact_info.website && (
                    <a
                      href={contact_info.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:border-primary-500 hover:text-primary-600 transition-colors"
                    >
                      {contact_info.website.replace('https://', '')}
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons - Side by Side */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={onReset}
                className="flex-1 px-8 py-3 bg-white border-2 border-primary-600 text-primary-600 rounded-full font-semibold hover:bg-primary-50 transition-colors"
              >
                ← Back to Claims
              </button>
              <a
                href={sales_pitch?.cta_url || 'https://plumhq.com/get-quote'}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 text-center px-8 py-3 bg-primary-600 text-white rounded-full font-semibold hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md"
              >
                Get Free Quote →
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  };

  export default SalesConversion;